#!/usr/bin/env python3
"""One Results call via HTTPS; API evidence, never browser/human acceptance.

Inspect first, then explicitly approve the inspected claim ID. Credentials stay
outside the checkout. No mock, retry, DB mutation, or forced chapter approval.
"""
import argparse
import base64
import hashlib
import http.cookiejar
import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--env-file', type=Path, required=True)
    p.add_argument('--accounts', type=Path, required=True)
    p.add_argument('--session', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--url', default='https://localhost:18443')
    p.add_argument('--approve-inspected-claim')
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit('Evidence exists; refusing overwrite')
    if a.accounts.stat().st_mode & 0o077:
        raise SystemExit('Account file must be private (0600)')
    env = dict(x.split('=', 1) for x in a.env_file.read_text().splitlines()
               if x and not x.startswith('#') and '=' in x)
    root = Path(env['PILOT_SECRETS_DIR'])
    user = (root / 'htpasswd').read_text().split(':', 1)[0]
    pw = (a.env_file.parent / 'gateway-password').read_text().strip()
    basic = 'Basic ' + base64.b64encode(f'{user}:{pw}'.encode()).decode()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(
        context=ssl.create_default_context(cafile=str(root / 'tls.crt'))),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    report = {'scope': 'API only. Browser NOT RUN. Operator approval is an automated test action, not human user acceptance.',
              'session_id': a.session, 'checks': [], 'results_requests': 0,
              'provider_usage': 'Not exposed by chapter response; not inferred from text length.'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    def save():
        a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    def call(label, path, method='GET', payload=None, expected=200):
        headers = {'Authorization': basic}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode()
            headers['Content-Type'] = 'application/json'
        start = time.monotonic()
        try:
            with opener.open(urllib.request.Request(a.url + '/api' + path,
                             data=data, headers=headers, method=method), timeout=900) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, body = e.code, e.read()
        try:
            parsed = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            parsed = body.decode('utf-8', errors='replace')
        report['checks'].append({'action': label, 'http_status': status,
            'elapsed_seconds': round(time.monotonic() - start, 3), 'expected_status': expected})
        save()
        if expected is not None and status != expected:
            # Error body may contain upstream configuration; never persist it.
            raise RuntimeError(f'{label}: HTTP {status}, expected {expected}')
        return parsed
    try:
        account = json.loads(a.accounts.read_text())[0]
        call('normal owner login', '/auth/login', 'POST', {k: account[k] for k in ('email', 'password')})
        base = f'/sessions/{a.session}'
        lab = call('read existing Card', base + '/research')
        report['expectation'] = lab.get('expectation')
        report['completed_specification_runs'] = sum(r.get('status') == 'ok' for r in lab.get('specification_runs', []))
        claim = lab.get('claim')
        if not claim:
            lab = call('draft bounded claim', base + '/research/claims/draft', 'POST')
            claim = lab.get('claim')
        report['inspected_claim'] = claim
        report['canonical_spec_id_before'] = lab.get('canonical_spec_id')
        save()
        if not a.approve_inspected_claim:
            return
        if not claim or claim['id'] != a.approve_inspected_claim or claim.get('stale'):
            raise RuntimeError('Inspected claim does not match fresh nonstale claim')
        call('approve inspected association claim', base + '/research/claims/' + claim['id'] + '/approve', 'POST')
        required = claim['provenance']['iv_spec_id']
        if lab.get('canonical_spec_id') != required:
            call('main analysis mismatch gate', base + '/research/prepare-paper', 'POST', expected=409)
            selected = next(r for r in reversed(lab['specification_runs']) if r['spec_id'] == required and r['status'] == 'ok')
            report['main_analysis_selection'] = {'reason': 'Use the completed comparable IV specification required by the inspected claim, retaining its identification limitations.',
                'run_id': selected['id'], 'spec_id': required}
            call('explicitly promote required completed IV', base + '/research/preview/promote', 'POST', {'run_id': selected['id']})
        call('prepare current approved research for paper', base + '/research/prepare-paper', 'POST')
        # Refresh is a normal cookie operation, with no bearer injection or path override.
        # Renewal failure was preserved in results-execution.json. This new normal
        # login is explicit recovery, not evidence that automatic renewal works.
        call('normal login before long generation', '/auth/login', 'POST', {k: account[k] for k in ('email', 'password')})
        report['results_requests'] = 1
        save()
        generated = call('one real Results generation and configured review', base + '/generate-chapter', 'POST',
                         {'chapter': {'type': 'results', 'title': 'Results'}})
        report['generation_response'] = generated
        chapter = generated.get('chapter', {})
        report['nonempty_results'] = bool((chapter.get('content') or '').strip())
        report['real_generation_and_review'] = (chapter.get('generation_source') == 'llm' and not chapter.get('generation_degraded')
            and generated.get('review_source') == 'llm' and not generated.get('review_degraded'))
        save()
        # Access may expire during the synchronous generation; normal refresh only.
        call('normal refresh after long generation', '/auth/refresh', 'POST', expected=None)
        call('normal login after long generation', '/auth/login', 'POST', {k: account[k] for k in ('email', 'password')})
        evidence = call('read Evidence backjump API target', base + '/evidence')
        report['evidence'] = evidence
        report['evidence_target_path'] = base + '/evidence'
        tex = call('export tex through gateway', base + '/doc-export?format=tex')
        if not isinstance(tex, str):
            raise RuntimeError('tex response is not text')
        tex_path = a.output.with_suffix('.tex')
        tex_path.write_text(tex)
        opened = tex_path.read_text()
        report['tex_opened'] = {'bytes': len(opened.encode()), 'sha256': hashlib.sha256(opened.encode()).hexdigest(),
            'document_environment': '\\begin{document}' in opened and '\\end{document}' in opened,
            'path': tex_path.name}
        report['outcome'] = 'API generation observed; inspect review and grounding outcomes separately; browser NOT RUN'
    except Exception as e:
        report['stopped'] = {'type': type(e).__name__, 'message': str(e) if isinstance(e, RuntimeError) else 'Transport or parsing failure; no retry.'}
    finally:
        save()


if __name__ == '__main__':
    main()
