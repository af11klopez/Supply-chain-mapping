from pathlib import Path
import json,re
r=Path(__file__).resolve().parents[1]
data=json.loads((r/'output/connection-routes.json').read_text());edges=data['edges'];nodes=data['nodes']
assert len(edges)==33
assert len({e['lane'] for e in edges})==len(edges)
for e in edges:
 for a,b in zip(e['points'],e['points'][1:]):
  assert a[0]==b[0] or a[1]==b[1],f'Non-orthogonal segment: {e["id"]}'
  for id,n in nodes.items():
   l,t,rt,bt=n['x']+.01,n['y']+.01,n['x']+n['w']-.01,n['y']+n['h']-.01
   if a[0]==b[0]:hit=l<a[0]<rt and max(min(a[1],b[1]),t)<min(max(a[1],b[1]),bt)
   else:hit=t<a[1]<bt and max(min(a[0],b[0]),l)<min(max(a[0],b[0]),rt)
   assert not hit,f'{e["id"]} intersects node {id}'
 for key,endpoint in [('from','source'),('to','target')]:
  n=nodes[e[key]];p=e[endpoint]
  assert abs(p[0]-n['x'])<.01 or abs(p[0]-n['x']-n['w'])<.01
  assert n['y']<=p[1]<=n['y']+n['h']
for i,e in enumerate(edges):
 for f in edges[i+1:]:
  for a,b in zip(e['points'],e['points'][1:]):
   for c,d in zip(f['points'],f['points'][1:]):
    if a[0]==b[0]==c[0]==d[0]:overlap=min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1]))
    elif a[1]==b[1]==c[1]==d[1]:overlap=min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0]))
    else:overlap=0
    assert overlap<.1,f'{e["id"]} and {f["id"]} overlap'
oldsvg=re.search(r'<svg\b[\s\S]*?</svg>',(r/'sources/original-viewer.html').read_text()).group()
assert oldsvg in (r/'output/combined-supply-chain.html').read_text()
print('33 routed connections: exact node endpoints, no node crossings, no collinear overlaps; original map unchanged.')
