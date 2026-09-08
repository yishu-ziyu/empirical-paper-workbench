"""Read-only session/research snapshot after normal account login. Output is private."""
import json,urllib.request,urllib.error,http.cookiejar,ssl,base64,hashlib,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description='API-only private persistence snapshot; does not replace browser acceptance')
parser.add_argument('--private-dir',required=True)
parser.add_argument('--accounts',required=True)
parser.add_argument('--origin',required=True)
parser.add_argument('--session',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
base=Path(args.private_dir)
account=json.loads(Path(args.accounts).read_text())[0]
username=(base/'secrets/htpasswd').read_text().split(':')[0];password=(base/'gateway-password').read_text().strip()
origin=args.origin;target=args.output
jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=str(base/'secrets/tls.crt'))),urllib.request.HTTPCookieProcessor(jar))
auth='Basic '+base64.b64encode((username+':'+password).encode()).decode()
def request(path,payload=None):
 req=urllib.request.Request(origin+'/api'+path,headers={'Authorization':auth,'Content-Type':'application/json'},data=None if payload is None else json.dumps(payload).encode())
 with opener.open(req,timeout=60) as r:return json.load(r)
request('/auth/login',{'email':account['email'],'password':account['password']})
sid=args.session
snapshot={p:request(p) for p in ('/sessions/'+sid,'/sessions/'+sid+'/research')}
Path(target).touch(mode=0o600,exist_ok=True);Path(target).chmod(0o600)
Path(target).write_text(json.dumps(snapshot,ensure_ascii=False,sort_keys=True,indent=2))
print(json.dumps({'normal_login':True,'session_id':sid,'endpoint_keys':{p:list(v) for p,v in snapshot.items()},'snapshot_sha256':hashlib.sha256(json.dumps(snapshot,ensure_ascii=False,sort_keys=True).encode()).hexdigest()}))
