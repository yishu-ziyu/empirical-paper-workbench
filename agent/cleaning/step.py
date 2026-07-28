from typing import Protocol, TypedDict


class StepReport(TypedDict, total=False):
    name: str
    status: str
    started_at: str
    duration: float
    report: dict


class CleaningStep(Protocol):
    name: str

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        ...
