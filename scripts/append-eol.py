from pathlib import Path
from collections import Counter,defaultdict
import json,re,html
from route_arrows import route,simplify
r=Path(__file__).resolve().parents[1]
original=(r/'sources/original-viewer.html').read_text()
layout=json.loads((r/'output/eol-layout.json').read_text())
original_nodes=json.loads((r/'output/original-layout.json').read_text())
W=7300;y=45150;nodes={};sections=[];positions={};owners={}
maxw=max(s['width'] for s in layout['sections'])
for s in layout['sections']:
 x=(W-s['width'])/2;positions[s['id']]=y
 svg=re.sub(r'<svg ',f'<svg style="position:absolute;left:{x}px;top:{y}px;width:{s["width"]}px!important;height:{s["height"]}px!important;max-width:none!important" ',s['svg'],count=1)
 start=svg.index('>');head=svg[:start];attrs=list(re.finditer(r' style="[^"]*"',head))
 for m in reversed(attrs[1:]):head=head[:m.start()]+head[m.end():]
 svg=head+svg[start:];sections.append(svg)
 for id,b in s['nodes'].items():
  nodes[id]={'x':x+b['x'],'y':y+b['y'],'w':b['w'],'h':b['h']};owners[id]=s['id']
 y+=s['height']+240
H=round(y+100)
returns=[('EOL_COSO4','N5_CO','Recovered cobalt sulfate → NMC pCAM feed'),('EOL_COSO4','A5_CO','Recovered cobalt sulfate → NCA pCAM feed'),('EOL_NISO4','N5_NI','Recovered nickel sulfate → NMC pCAM feed'),('EOL_NISO4','A5_NI','Recovered nickel sulfate → NCA pCAM feed'),('EOL_MHP','R4_C1','Recovered MHP → mixed hydroxide refining'),('EOL_NMCPCAM','N6_PC','Qualified recycled NMC precursor → NMC CAM'),('EOL_NMCCAM','C7_NMC','Qualified regenerated NMC CAM → cathode manufacture'),('EOL_NCACAM','C7_NCA','Qualified regenerated NCA CAM → cathode manufacture'),('EOL_LIOH','N6_LI','Qualified recovered LiOH → NMC CAM feed'),('EOL_LIOH','A6_LI','Qualified recovered LiOH → NCA CAM feed'),('EOL_GRAPH','C7_GR','Qualified recycled graphite → anode feed'),('EOL_CUFOIL','C7_CU','Qualified recycled copper foil → anode current collector'),('EOL_ALFOIL','C7_AL','Qualified recycled aluminium foil → cathode current collector')]
allnodes={**original_nodes,**nodes};edges=[]
for i,e in enumerate(layout['edges']):edges.append({**e,'id':f'P{i+1:02}','kind':'process','side':'right','lane':(W+maxw)/2+100+i*38})
for i,(a,b,label) in enumerate(returns):edges.append({'from':a,'to':b,'label':label,'dashed':True,'id':f'R{i+1:02}','kind':'recovery','side':'left','lane':-160-i*64})
counts=Counter((e[key],e['side']) for e in edges for key in ['from','to']);indices=defaultdict(int);used=[];paths=[];audit=[]
def port(id,side):
 b=allnodes[id];key=(id,side);indices[key]+=1
 return (b['x']+(b['w'] if side=='right' else 0),b['y']+b['h']*indices[key]/(counts[key]+1))
def branch(id,p,lane,side):
 sign=1 if side=='right' else -1;stub=(p[0]+sign*14,p[1]);end=(lane,p[1])
 if id in nodes:obstacles=[b for name,b in nodes.items() if owners[name]==owners[id]]
 else:obstacles=[b for b in original_nodes.values() if b['y']+b['h']>p[1]-400 and b['y']<p[1]+400]
 result=simplify([p]+route(stub,end,obstacles,used))
 used.extend(zip(result,result[1:]));return result
for e in edges:
 a=port(e['from'],e['side']);b=port(e['to'],e['side']);left=branch(e['from'],a,e['lane'],e['side']);right=branch(e['to'],b,e['lane'],e['side'])
 pts=simplify(left+list(reversed(right)))
 d='M '+' L '.join(f'{x:.3f} {y:.3f}' for x,y in pts);color='#278473' if e['kind']=='recovery' else '#596677';label=e['label'] or e['from']+' → '+e['to'];dash='stroke-dasharray="8 5"' if e['dashed'] else ''
 title=html.escape(e['id']+' · '+label);badges=[]
 # Put the matching endpoint IDs beside the outer rail, away from process nodes.
 for px,py in [(e['lane'],a[1]),(e['lane'],b[1])]:
  badges.append(f'<g><rect x="{px-17}" y="{py-22}" width="34" height="17" rx="4" fill="white" stroke="{color}"/><text x="{px}" y="{py-10}" text-anchor="middle" font-family="Arial" font-size="10" fill="{color}">{e["id"]}</text></g>')
 paths.append(f'<g class="connection {e["kind"]}" data-connection="{e["id"]}"><title>{title}</title><path d="{d}" fill="none" stroke="white" stroke-width="5" opacity=".9"/><path class="connection-line" d="{d}" fill="none" stroke="{color}" stroke-width="1.9" {dash} marker-end="url(#arrow-{e["kind"]})" style="pointer-events:stroke;cursor:pointer"/>{"".join(badges)}</g>')
 audit.append({**e,'points':pts,'source':a,'target':b});print('Routed',e['id'],e['from'],'→',e['to'],flush=True)
# The original vehicle handoffs retain their geometry.
for id,sx in [('EOL_IN_NMC',3335.337502161662),('EOL_IN_NCA',3555.337502161662)]:
 b=nodes[id];tx=b['x']+b['w']/2;ty=b['y'];middle=44800 if id.endswith('NMC') else 44900
 paths.append(f'<path d="M {sx} 44576 V {middle} H {tx} V {ty}" fill="none" stroke="#596677" stroke-width="1.7" marker-end="url(#arrow-process)"/>')
MINX=-1100
markers=''.join(f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>' for kind,color in [('process','#596677'),('recovery','#278473')])
connections=f'<svg id="eol-connections" xmlns="http://www.w3.org/2000/svg" width="{W-MINX}" height="{H}" viewBox="{MINX} 0 {W-MINX} {H}" style="position:absolute;left:{MINX}px;top:0;width:{W-MINX}px!important;height:{H}px!important;pointer-events:none;overflow:visible"><defs>{markers}</defs>'+''.join(paths)+'</svg>'
page=original.replace('#art svg{','#art > svg:first-of-type{');end=page.index('</svg>')+len('</svg>');page=page[:end]+''.join(sections)+connections+page[end:]
page=page.replace('const W=7300,H=44750;',f'const W=7300,H={H};')
page=page.replace('scale=Math.min((innerWidth-40)/W,(innerHeight-40)/H);tx=(innerWidth-W*scale)/2;',f'scale=Math.min((innerWidth-40)/{W-MINX},(innerHeight-40)/H);tx=(innerWidth-{W-MINX}*scale)/2-({MINX})*scale;')
page=page.replace('scale=(innerWidth-40)/W;tx=20;',f'scale=(innerWidth-40)/{W-MINX};tx=20-({MINX})*scale;')
page=page.replace('Complete cobalt-to-EV process map','Complete cobalt-to-EV + EOL process map').replace('All nine tiers · original Mermaid nodes and links · vector zoom','Original map preserved · EOL process links: P · Material returns: R')
page=page.replace('</select>', ''.join(f'<option value="{s["id"]}">{html.escape(s["title"])}</option>' for s in layout['sections'])+'</select>',1)
page=page.replace('t9:37800}', 't9:37800,'+','.join(f'{id}:{round(y)}' for id,y in positions.items())+'}')
options=''.join(f'<option value="{e["id"]}">{html.escape(e["id"]+" · "+(e["label"] or e["from"]+" → "+e["to"]))}</option>' for e in edges)
page=page.replace('<div id="help">',f'<div><select id="connection-picker" aria-label="Follow a connection"><option value="">Follow a connection…</option>{options}</select><button id="connection-source">Origin</button><button id="connection-target">Destination</button><button id="connection-reset">Show all</button></div><div id="help">')
page=page.replace('</style>', '#panel select{max-width:100%}.connection.dim{opacity:.08}.connection.active .connection-line{stroke-width:4}.connection.active{opacity:1}</style>',1)
metadata={e['id']:{'source':e['source'],'target':e['target']} for e in audit}
extra='''
<script>(()=>{const points=METADATA;const picker=document.getElementById('connection-picker');
function select(id){picker.value=id;document.querySelectorAll('.connection').forEach(g=>{g.classList.toggle('dim',!!id&&g.dataset.connection!==id);g.classList.toggle('active',g.dataset.connection===id)});}
function go(which){const p=points[picker.value]?.[which];if(!p)return;window.focusConnectionPoint(p[0],p[1]);}
picker.onchange=()=>{select(picker.value);go('source')};document.getElementById('connection-source').onclick=()=>go('source');document.getElementById('connection-target').onclick=()=>go('target');document.getElementById('connection-reset').onclick=()=>select('');document.querySelectorAll('.connection-line').forEach(p=>p.addEventListener('click',()=>select(p.parentElement.dataset.connection)));})();</script>
'''.replace('METADATA',json.dumps(metadata))
page=page.replace('fitAll();})();','window.focusConnectionPoint=(x,y)=>{scale=.85;tx=innerWidth*.60-x*scale;ty=innerHeight*.42-y*scale;apply()};fitAll();})();')
page=page.replace('</body>',extra+'</body>');(r/'output/combined-supply-chain.html').write_text(page)
a=(r/'sources/full-map.mmd').read_text().strip();b=re.sub(r'^flowchart TB\s*','',(r/'sources/eol.mmd').read_text().strip())
recovery='\n'.join(f'{a} -.->|"{label}; destination qualification required"| {b}' for a,b,label in returns)
(r/'combined-supply-chain.mmd').write_text(a+'\n\n'+b+'\n\n%% Vehicle handoff\nE9_EVNMC --> EOL_IN_NMC\nE9_EVNCA --> EOL_IN_NCA\n\n%% Qualified recovered-material return points\n'+recovery+'\n')
oldsvg=re.search(r'<svg\b[\s\S]*?</svg>',original).group();assert oldsvg in page
svgparts=[]
for section in sections:
 m=re.search(r'left:([\d.]+)px;top:([\d.]+)px',section);svgparts.append(section.replace('<svg ',f'<svg x="{m[1]}" y="{m[2]}" ',1))
# In an SVG export, the overlay's nested viewport starts at the minimum X.
svgconnections=connections.replace('<svg id=',f'<svg x="{MINX}" y="0" id=',1)
(r/'output/combined-supply-chain.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W-MINX}" height="{H}" viewBox="{MINX} 0 {W-MINX} {H}">'+oldsvg+''.join(svgparts)+svgconnections+'</svg>')
(r/'output/connection-routes.json').write_text(json.dumps({'edges':audit,'nodes':allnodes},indent=2))
print('Original SVG preserved byte for byte; 20 EOL routes and 13 material returns connected.')
