import json,urllib.request,urllib.error,threading,subprocess,os
from pathlib import Path
base='http://127.0.0.1:8787/api/sync'
token='test-'+os.urandom(24).hex()
data=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./src/core.js').empty()))"],cwd=Path(__file__).resolve().parents[1]))
def req(method='GET',body=None,version=None,key=token,origin=None):
    headers={'Authorization':'Bearer '+key}
    if origin:headers['Origin']=origin
    if body is not None:headers.update({'Content-Type':'application/json','If-Match':str(version)})
    r=urllib.request.Request(base,data=json.dumps(body).encode() if body else None,headers=headers,method=method)
    try:
        with urllib.request.urlopen(r) as result:return result.status,json.load(result)
    except urllib.error.HTTPError as e:return e.code,json.load(e)
assert req()[0]==404
assert req('PUT',data,0)[1]['version']==1
assert req()[1]['data']==data
assert req('PUT',data,0)[0]==409
assert req(key='wrong')[0]==401
assert req(origin='https://unknown.invalid')[0]==403
assert req('PUT',{'schemaVersion':2},1)[0]==400
results=[]
threads=[threading.Thread(target=lambda:results.append(req('PUT',data,1)[0])) for i in range(2)]
for t in threads:t.start()
for t in threads:t.join()
assert sorted(results)==[200,409],results
assert req(key='different-'+os.urandom(24).hex())[0]==404
for path in ['/rota-sync.sqlite3','/server.py','/../server.py']:
    try:urllib.request.urlopen('http://127.0.0.1:8787'+path);raise AssertionError(path)
    except urllib.error.HTTPError as e:assert e.code==404
print('PASS: sync read/write, isolation, authorization, invalid data, origin, stale version, concurrent race, static allowlist')
