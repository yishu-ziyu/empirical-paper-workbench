"""Fail closed on pinned Card bytes; optionally run real packaged OLS/IV.

Build: python scripts/check_card_package.py --fetch --data-only
Container smoke: python scripts/check_card_package.py
This is dependency evidence, not a substitute for a persisted application run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--data-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'deploy/dependencies-card.json').read_text())
    path = Path(os.environ['ECONPAPER_CARD_CSV'])
    if args.fetch:
        with urllib.request.urlopen(manifest['card_url'], timeout=60) as response:
            payload = response.read()
    else:
        payload = path.read_bytes()
    checksum = hashlib.sha256(payload).hexdigest()
    assert checksum == manifest['card_sha256'], 'Card checksum mismatch'
    rows = list(csv.reader(io.StringIO(payload.decode('utf-8'))))
    assert rows[0] == manifest['raw_columns'], 'Card columns mismatch'
    assert len(rows) - 1 == manifest['rows'], 'Card row count mismatch'
    if args.fetch:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    report = {'card_sha256': checksum, 'rows': len(rows) - 1, 'data_columns': len(rows[0]) - 1}
    if not args.data_only:
        import pandas as pd
        import statspai as sp

        distribution = importlib.metadata.distribution('StatsPAI')
        assert distribution.version == manifest['statspai_version']
        direct = json.loads(distribution.read_text('direct_url.json') or '{}')
        assert not direct.get('dir_info', {}).get('editable'), 'Editable StatsPAI prohibited'
        assert direct.get('archive_info', {}).get('hashes', {}).get('sha256') == manifest['archive_sha256'], 'StatsPAI source archive mismatch'
        df = pd.read_csv(path).drop(columns=manifest['discard_columns'])
        controls = 'exper + expersq + black + smsa + south + smsa66 + ' + ' + '.join(f'reg66{i}' for i in range(1, 9))
        specs = [('ols_region_dummies', 'lwage ~ educ + ' + controls, sp.feols, {'vcov': 'HC1'}), ('iv_region_dummies', 'lwage ~ (educ ~ nearc4) + ' + controls, sp.ivreg, {})]
        results = []
        for identifier, formula, estimate, kwargs in specs:
            result = estimate(formula, data=df, **kwargs)
            coef, se = float(result.params['educ']), float(result.std_errors['educ'])
            assert math.isfinite(coef) and math.isfinite(se) and se > 0
            results.append({'spec_id': identifier, 'formula': formula, 'coef': coef, 'se': se, 'n': len(df), 'status': 'ok'})
        report.update(statspai_version=distribution.version, statspai_revision=manifest['statspai_revision'], estimates=results)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
