#!/usr/bin/env python3
"""Feed an existing public chapter to a rebuilt container for one read-only review.

Usage: python3 results-component-check.py CONTAINER OUTPUT.json
No session writes, generation, approval, provider response-body logging or retry.
"""
import json
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
source = json.loads((here / 'results-real-once.json').read_text())
payload = {
    'content': source['generation_response']['chapter']['content'],
    'direction': source['evidence']['specification']['question'],
}
output = Path(sys.argv[2])
if output.exists():
    raise SystemExit('Refusing to overwrite evidence')
code = '''
import contextlib, hashlib, io, json, time
payload = PAYLOAD
report = {'scope': 'Read-only component diagnostic, NOT product API/browser journey. Saved chapter unchanged and unapproved.', 'calls': 1, 'structured_retries': 0, 'content_sha256': hashlib.sha256(payload['content'].encode()).hexdigest()}
captured = io.StringIO()
start = time.monotonic()
try:
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        from agent.llm.router import router
        from agent.nodes.review_chapter import invoke_review_llm
        from agent.protocols import ReviewRubric
        config = router.get_config('review')
        if config.provider == 'mock':
            raise RuntimeError('Mock configuration rejected')
        result = invoke_review_llm(config, payload['content'], ReviewRubric(), payload['direction'], [], claim='association', structured_retries=0)
    report['review_source'] = 'llm'
    report['review_typed'] = True
    report['review_degraded'] = False
    report['result'] = result
except Exception as exc:
    report['exception_type'] = type(exc).__name__
    status = getattr(exc, 'status_code', None)
    if isinstance(status, int): report['http_status'] = status
    report['review_source'] = 'failed_real_attempt'
    report['review_typed'] = False
report['elapsed_seconds'] = round(time.monotonic() - start, 3)
report['usage'] = 'invoke_review_llm returns typed output only; usage and provider request IDs not exposed'
print(json.dumps(report, ensure_ascii=False))
'''.replace('PAYLOAD', repr(payload))
try:
    r = subprocess.run(['docker', 'exec', '-i', sys.argv[1], 'python', '-'],
                       input=code, text=True, capture_output=True, timeout=180)
except subprocess.TimeoutExpired:
    output.write_text(json.dumps({'scope': 'component diagnostic', 'exception_type': 'TimeoutExpired', 'calls': 1, 'no_retry': True}) + '\n')
    raise SystemExit('Component diagnostic timed out; failure preserved')
if r.returncode:
    report = {'scope': 'component diagnostic', 'process_exit_code': r.returncode,
              'error': 'Container command failed; unfiltered output suppressed'}
else:
    report = json.loads(r.stdout)
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
