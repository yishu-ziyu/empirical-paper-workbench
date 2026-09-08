#!/usr/bin/env python3
"""API-only pilot evidence. Never substitutes for browser acceptance.

Uses standard-library cookie policy, real application login and the TLS gateway.
No cookie-path override, Bearer injection, write retry, or provider success claim.
Credentials and response bodies never enter the evidence output.
"""
import argparse
import base64
import hashlib
import http.cookiejar
import http.client
import json
import os
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='https://localhost:18443')
    p.add_argument('--env-file', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to overwrite first evidence; choose a new output.')
    env = dict(line.split('=', 1) for line in args.env_file.read_text().splitlines()
               if line and not line.startswith('#') and '=' in line)
    root = Path(env['PILOT_SECRETS_DIR'])
    # Passwords only live in memory; htpasswd username is public test identity.
    username = (root / 'htpasswd').read_text().split(':', 1)[0]
    gateway_password = (args.env_file.parent / 'gateway-password').read_text().strip()
    basic = 'Basic ' + base64.b64encode(f'{username}:{gateway_password}'.encode()).decode()
    context = ssl.create_default_context(cafile=str(root / 'tls.crt'))
    report = {'scope': 'API only; browser NOT RUN; real LLM NOT configured',
              'url': args.url, 'started_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'checks': [], 'limitations': ['Cookie policy is Python CookieJar, not browser evidence.',
              'No access-expiry renewal success or real chapter generation claimed.']}

    def save():
        for entry in report['checks']:
            label = entry['check']
            if 'frames' in entry:
                entry['expectation'] = 'HTTP 200, terminal run.succeeded, SUCCEEDED status and nonempty result'
                run = entry.get('run', {})
                entry['outcome'] = ('pass' if entry.get('http_status') == 200 and
                    run.get('status') == 'SUCCEEDED' and run.get('result_present') and
                    'run.succeeded' in entry.get('terminal_event_types', []) else 'not_run' if not run else 'fail')
                continue
            if 'refresh' in label and entry.get('http_status') == 401:
                entry['expectation'] = 'Refresh should return 200 for normal renewal'
                entry['outcome'] = 'known_reproduced_failure'
                continue
            expected = [200]
            if 'gateway denial' in label or 'after logout' in label or 'anonymous session creation' in label or 'anonymous upload denied' in label:
                expected = [401]
            elif 'forbidden' in label or 'capability isolation' in label:
                expected = [401, 403, 404]
            elif label.endswith('register'):
                expected = [201]
            elif 'admission' in label or label == 'upload greater than 1 MiB' or label == 'owner upload resolution':
                expected = [202]
            elif 'over product' in label or 'Content-Length' in label or 'header limit probe' in label:
                expected = [413]
            elif 'check identity' in label and entry.get('http_status') == 401:
                entry['expectation'] = 'Expired access interrupts identity check; normal re-login required'
                entry['outcome'] = 'known_reproduced_failure'
                continue
            entry['expectation'] = 'HTTP ' + '/'.join(str(x) for x in expected)
            entry['outcome'] = 'pass' if entry.get('http_status') in expected else 'fail'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')

    def client():
        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context),
                                            urllib.request.HTTPCookieProcessor(jar))
        return opener, jar

    def request(c, label, path, method='GET', payload=None, headers=None, gateway=True, raw=None):
        h = {'Authorization': basic} if gateway else {}
        h.update(headers or {})
        data = raw
        if payload is not None:
            data = json.dumps(payload).encode()
            h['Content-Type'] = 'application/json'
        req = urllib.request.Request(args.url + path, data=data, headers=h, method=method)
        started = time.monotonic()
        try:
            with c[0].open(req, timeout=90) as r:
                body, status, rh = r.read(), r.status, r.headers
        except urllib.error.HTTPError as e:
            body, status, rh = e.read(), e.code, e.headers
        except Exception as e:
            report['checks'].append({'check': label, 'transport_error_type': type(e).__name__})
            save()
            return None, {}
        try:
            result = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            result = {}
        safe_detail = result.get('detail') if isinstance(result, dict) else None
        allowed_details = {'Missing refresh token', 'Not authenticated', 'Upload not found',
                           'Session not found', 'Forbidden', 'File exceeds 50MB upload limit'}
        entry = {'check': label, 'method': method, 'path': path, 'http_status': status,
                 'elapsed_seconds': round(time.monotonic() - started, 3),
                 'response_bytes': len(body)}
        if isinstance(safe_detail, str) and safe_detail in allowed_details:
            entry['detail'] = safe_detail
        if label.endswith('login'):
            entry['access_token_body_empty'] = result.get('access_token') == ''
            entry['cookie_attributes'] = [{'name': x.name, 'path': x.path, 'secure': x.secure,
                'http_only': x.has_nonstandard_attr('HttpOnly')} for x in c[1]]
        report['checks'].append(entry)
        save()
        return status, result

    a, b, anon = client(), client(), client()
    for path in ('/', '/api/auth/me', '/api/sessions'):
        request(anon, 'gateway denial ' + path, path, gateway=False)
    request(anon, 'anonymous session creation denied', '/api/sessions', 'POST')
    accounts = []
    for label, c in [('a', a), ('b', b)]:
        suffix = secrets.token_hex(8)
        account = {'email': f'pilot-{suffix}@example.invalid', 'username': f'pilot-{suffix}',
                   'password': secrets.token_urlsafe(30)}
        accounts.append(account)
        private_accounts = args.env_file.parent / (args.output.stem + '-accounts.json')
        with os.fdopen(os.open(private_accounts, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
            json.dump(accounts, f)
        status, _ = request(c, label + ' register', '/api/auth/register', 'POST', account)
        if status != 201:
            report['stopped'] = 'Registration failed; no login retries.'
            save()
            return 1
        status, _ = request(c, label + ' login', '/api/auth/login', 'POST',
                            {k: account[k] for k in ('email', 'password')})
        if status != 200:
            report['stopped'] = 'Login failed; no retries.'
            save()
            return 1
        request(c, label + ' authenticated me', '/api/auth/me')
    probe = urllib.request.Request(args.url + '/api/auth/refresh')
    a[1].add_cookie_header(probe)
    report['refresh_cookie_policy'] = {
        'jar_refresh_paths': [x.path for x in a[1] if x.name == 'ep_refresh'],
        'refresh_sent_to_api_auth_refresh': 'ep_refresh=' in (probe.get_header('Cookie') or '')}
    request(a, 'first refresh through actual proxy', '/api/auth/refresh', 'POST')

    def ensure_login(c, account, label):
        status, _ = request(c, label + ' check identity', '/api/auth/me')
        if status == 401:
            request(c, label + ' expired refresh attempt', '/api/auth/refresh', 'POST')
            request(c, label + ' normal re-login', '/api/auth/login', 'POST',
                    {k: account[k] for k in ('email', 'password')})

    def observe_stream(rid, label):
        entry = {'check': label, 'run_id': rid, 'frames': []}
        report['checks'].append(entry)
        started = time.monotonic()
        req = urllib.request.Request(args.url + '/api/runs/' + rid + '/events',
                                     headers={'Authorization': basic, 'Accept': 'text/event-stream'})
        try:
            with a[0].open(req, timeout=120) as response:
                entry['http_status'] = response.status
                for line in response:
                    if line.startswith(b'data: '):
                        event = json.loads(line[6:])
                        frame = {k: event.get(k) for k in ('seq', 'type', 'status', 'attempt', 'node', 'spec_id') if k in event}
                        frame['arrival_seconds'] = round(time.monotonic() - started, 3)
                        entry['frames'].append(frame)
                        save()
                    if time.monotonic() - started > 120:
                        entry['observation_deadline_reached'] = True
                        break
        except urllib.error.HTTPError as e:
            entry['http_status'] = e.code
        except Exception as e:
            entry['transport_error_type'] = type(e).__name__
        ensure_login(a, accounts[0], label + ' after stream')
        status, run = request(a, label + ' terminal read', '/api/runs/' + rid)
        entry['run'] = {k: run.get(k) for k in ('status', 'attempt', 'error')}
        entry['run']['result_present'] = run.get('result') is not None
        entry['terminal_event_types'] = [f['type'] for f in entry['frames'] if f.get('type') in ('run.succeeded', 'run.failed', 'run.cancelled')]
        save()
        return run.get('status') == 'SUCCEEDED'

    status, card = request(a, 'Card admission', '/api/demos/card', 'POST',
                           headers={'Idempotency-Key': secrets.token_hex(20)})
    if status == 202:
        sid, rid = card['session_id'], card['run_id']
        report['card_resources'] = {'session_id': sid, 'upload_run_id': rid}
        if observe_stream(rid, 'Card bootstrap SSE'):
            status, _ = request(a, 'Card freeze', f'/api/sessions/{sid}/research/specification-space/freeze', 'POST')
            if status == 200:
                status, run = request(a, 'Card specification execution admission',
                    f'/api/sessions/{sid}/research/specification-space/run', 'POST',
                    headers={'Idempotency-Key': secrets.token_hex(20)})
                if status == 202:
                    report['card_resources']['spec_run_id'] = run['run_id']
                    observe_stream(run['run_id'], 'Card specification SSE')
            status, lab = request(a, 'Card research result', f'/api/sessions/{sid}/research')
            if status == 200:
                runs = lab.get('specification_runs', [])
                report['card_results'] = {
                    'completed_specification_runs': sum(x.get('status') == 'ok' for x in runs),
                    'total_specification_runs': len(runs),
                    'provenance': lab.get('provenance'),
                    'runs': [{k: x.get(k) for k in ('id', 'spec_id', 'status', 'coef', 'se', 'n', 'estimator', 'formula', 'covariance', 'producer_run_id')} for x in runs]}
    ensure_login(a, accounts[0], 'before isolation a')
    ensure_login(b, accounts[1], 'before isolation b')

    csv = b'x,y,z\n' + b'1,2,3\n' * 200000
    boundary = 'pilot-' + secrets.token_hex(12)
    def multipart(content):
        return (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="synthetic.csv"\r\nContent-Type: text/csv\r\n\r\n'.encode()
                + content + f'\r\n--{boundary}--\r\n'.encode())
    upload_key = secrets.token_hex(20)
    headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary, 'Idempotency-Key': upload_key}
    report['synthetic_csv'] = {'bytes': len(csv), 'rows': 200000, 'columns': ['x', 'y', 'z'],
                             'sha256': hashlib.sha256(csv).hexdigest()}
    status, admission = request(a, 'upload greater than 1 MiB', '/api/upload', 'POST', headers=headers, raw=multipart(csv))
    if status == 202:
        sid, rid = admission['session_id'], admission['run_id']
        report['owned_resources'] = {'session_id': sid, 'run_id': rid}
        for label, c in [('anonymous', anon), ('other account', b)]:
            for path in (f'/api/sessions/{sid}', f'/api/runs/{rid}', f'/api/runs/{rid}/events',
                         f'/api/sessions/{sid}/export?format=tex', f'/api/sessions/{sid}/artifacts'):
                request(c, label + ' forbidden read', path)
            request(c, label + ' forbidden mutation', f'/api/sessions/{sid}/research/specification-space/freeze', 'POST')
            request(c, label + ' forbidden delete', f'/api/sessions/{sid}', 'DELETE')
            request(c, label + ' upload capability isolation', '/api/upload/resolve', 'POST',
                    headers={'Idempotency-Key': upload_key})
        request(a, 'owner session after forbidden deletes', f'/api/sessions/{sid}')
        request(a, 'owner upload resolution', '/api/upload/resolve', 'POST', headers={'Idempotency-Key': upload_key})
        status, run = request(a, 'owner current run', f'/api/runs/{rid}')
        report['run_observation'] = {k: run.get(k) for k in ('status', 'attempt')}
        report['run_observation']['error_present'] = bool(run.get('error'))
        report['run_observation']['result_present'] = run.get('result') is not None
    request(anon, 'anonymous upload denied', '/api/upload', 'POST', headers={**headers, 'Idempotency-Key': secrets.token_hex(20)}, raw=multipart(b'x,y\n1,2\n'))
    request(a, 'upload over product and gateway limits', '/api/upload', 'POST', headers={**headers, 'Idempotency-Key': secrets.token_hex(20)}, raw=multipart(b'x\n' + b'1\n' * (26 * 1024 * 1024)))
    # Separate Content-Length rejection probe: do not resend a failed write.
    parsed = urllib.parse.urlsplit(args.url)
    connection = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, context=context, timeout=10)
    try:
        connection.putrequest('POST', '/api/upload')
        connection.putheader('Authorization', basic)
        connection.putheader('Content-Length', str(52 * 1024 * 1024))
        connection.endheaders()
        response = connection.getresponse()
        report['checks'].append({'check': 'gateway rejects over-limit Content-Length before body',
                                 'http_status': response.status, 'declared_bytes': 52 * 1024 * 1024,
                                 'body_sent_bytes': 0})
    except Exception as e:
        report['checks'].append({'check': 'gateway header limit probe', 'transport_error_type': type(e).__name__})
    finally:
        connection.close()
    ensure_login(a, accounts[0], 'before logout')
    request(a, 'logout', '/api/auth/logout', 'POST')
    request(a, 'after logout protected me', '/api/auth/me')
    report['completed_at_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    save()
    card_results = report.get('card_results', {})
    report['card_evaluation'] = {
        'expectation': 'At least two completed specification runs with actual coefficient, SE and n',
        'outcome': 'pass' if card_results.get('completed_specification_runs', 0) >= 2 and
            all(x.get('coef') is not None and x.get('se') is not None and x.get('n') for x in card_results.get('runs', [])) else 'fail'}
    report['overall'] = 'incomplete: browser, normal renewal and real LLM journey not accepted'
    save()
    print(json.dumps({'evidence': str(args.output), 'checks': len(report['checks']), 'browser': 'NOT RUN',
                      'outcomes': {key: sum(x.get('outcome') == key for x in report['checks'])
                                   for key in ('pass', 'fail', 'known_reproduced_failure', 'not_run')},
                      'card': report['card_evaluation']['outcome']}))
    return 1


if __name__ == '__main__':
    sys.exit(main())
