import json, urllib.request, urllib.error

BASE='http://127.0.0.1:8096/api/void/'
def post(endpoint,data,admin=False):
    headers={'Content-Type':'application/json'}
    if admin: headers['X-Admin-Key']='0101'
    req=urllib.request.Request(BASE+endpoint,json.dumps(data).encode(),headers)
    try:
        with urllib.request.urlopen(req,timeout=5) as res:return res.status,json.load(res)
    except urllib.error.HTTPError as e:return e.code,json.load(e)

assert post('team_reset',{'team':11,'confirm':'AGAIN'},True)[0]==200
for i in range(10):
    assert post('quest',{'team':11,'dev':f'limit{i}','done':[]})[0]==200
status,data=post('quest',{'team':11,'dev':'limit10','done':[]})
assert status==400 and '10대' in json.dumps(data,ensure_ascii=False),(status,data)
print('OK eleventh device receives a readable 400 response')
assert post('quest',{'team':11,'dev':'limit0','done':['q1']})[0]==200
print('OK registered device can still save progress at capacity')
assert post('team_reset',{'team':11,'confirm':'AGAIN'},True)[0]==200
