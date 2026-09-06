"""Card teaching-case boot: real extract through the existing upload pipeline."""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from config import PRODUCT_ROOT, settings
from run_repository import (
    IdempotencyConflict,
    QueueFull,
    RunRepository,
    UploadAdmission,
    finalize_upload_fingerprint,
)
from services.research_lab import (
    CARD_CITATION,
    CARD_REDISTRIBUTION,
    REQUIRED_CARD_COLUMNS,
    extract_kind_for,
    seed_card_lab,
)
from upload_artifacts import publish_normalized_upload, remove_owned_upload


CARD_FILENAME = "card_1995.csv"


def _force_nine_col() -> bool:
    raw = (os.getenv("ECONPAPER_CARD_EXTRACT") or "").strip().lower()
    return raw in {"statspai_card_9", "9", "nine"}


def _candidate_wooldridge_paths() -> list[Path]:
    paths: list[Path] = []
    env_path = (os.getenv("ECONPAPER_CARD_CSV") or "").strip()
    if env_path:
        paths.append(Path(env_path).expanduser())
    if _force_nine_col():
        return paths if env_path else []
    try:
        import statspai

        root = Path(statspai.__file__).resolve().parents[2]
        paths.append(root / "papers" / "data_card1995.csv")
    except Exception:
        pass
    paths.append(
        PRODUCT_ROOT.parent
        / "dependencies"
        / "StatsPAI"
        / "papers"
        / "data_card1995.csv"
    )
    return paths


def _drop_index_columns(df: pd.DataFrame) -> pd.DataFrame:
    drop = [col for col in df.columns if str(col).lower() in {"rownames", "unnamed: 0"}]
    return df.drop(columns=drop) if drop else df


def load_card_extract() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load Card extract: env/path → 34-col sibling CSV → StatsPAI 9-col subset."""
    if not _force_nine_col():
        for path in _candidate_wooldridge_paths():
            if path.is_file():
                df = _drop_index_columns(pd.read_csv(path))
                columns = [str(col) for col in df.columns]
                checksum = hashlib.sha256(path.read_bytes()).hexdigest()
                provenance = {
                    "source": "statspai:papers/data_card1995.csv",
                    "citation": CARD_CITATION,
                    "checksum": checksum,
                    "redistribution": CARD_REDISTRIBUTION,
                    "extract_kind": extract_kind_for(columns),
                }
                return df, provenance

    try:
        from statspai.datasets import card_1995
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Card extract is unavailable",
        ) from exc

    df = _drop_index_columns(card_1995(simulated=False))
    columns = [str(col) for col in df.columns]
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    provenance = {
        "source": "statspai.datasets.card_1995(simulated=False)",
        "citation": CARD_CITATION,
        "checksum": hashlib.sha256(csv_bytes).hexdigest(),
        "redistribution": CARD_REDISTRIBUTION,
        "extract_kind": extract_kind_for(columns),
    }
    return df, provenance


def _validate_extract(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_CARD_COLUMNS if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Card extract missing columns: {', '.join(missing)}",
        )
    if len(df) != 3010:
        raise HTTPException(
            status_code=503,
            detail=f"Card extract expected 3010 rows, got {len(df)}",
        )


async def admit_card_upload(
    *,
    user_id: int | None,
    idempotency_key: str,
) -> tuple[UploadAdmission, bytes]:
    """Create a session and admit Card bytes on the existing upload pipeline."""
    from routers.sessions import _normalize_dataframe

    df, provenance = await run_in_threadpool(load_card_extract)
    _validate_extract(df)
    csv_bytes, dataset_meta = await run_in_threadpool(
        _normalize_dataframe, df, CARD_FILENAME
    )
    fingerprint = finalize_upload_fingerprint(
        hashlib.sha256(csv_bytes), CARD_FILENAME
    )
    lab = seed_card_lab(columns=list(dataset_meta.columns), provenance=provenance)

    session_id = str(uuid.uuid4())
    csv_path: Path | None = None
    try:
        csv_path = await run_in_threadpool(
            publish_normalized_upload,
            csv_bytes,
            session_id=session_id,
            upload_dir=Path(settings.UPLOAD_DIR),
        )
        lab["extract_csv_path"] = str(csv_path)
        initial_state = {
            "session_id": session_id,
            "csv_path": str(csv_path),
            "uploaded_datasets": [{"path": str(csv_path), "format": "csv"}],
            "research_lab": lab,
        }
        admission = await RunRepository().admit_upload(
            session_id=session_id,
            user_id=user_id,
            csv_path=str(csv_path),
            dataset_meta=dataset_meta.model_dump(),
            initial_state=initial_state,
            idempotency_key=idempotency_key,
            input_fingerprint=fingerprint,
        )
    except IdempotencyConflict as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=409, detail="upload_request_conflict") from exc
    except QueueFull as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(
            status_code=429,
            detail="run queue is full",
            headers={"Retry-After": "5"},
        ) from exc
    except HTTPException:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise
    except Exception as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=500, detail="upload_admission_failed") from exc

    if admission.replayed and csv_path is not None:
        remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
    return admission, csv_bytes
