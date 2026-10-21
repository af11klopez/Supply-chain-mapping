const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});try{const page=await browser.newPage();await page.setContent('<!doctype html><body></body>');await page.addScriptTag({path:require.resolve('mermaid/dist/mermaid.js')});
const src=fs.readFileSync(path.join(root,'sources/eol.mmd'),'utf8');
const result=await page.evaluate(async src=>{
mermaid.initialize({startOnLoad:false,securityLevel:'strict',maxTextSize:200000,maxEdges:5000,look:'neo',theme:'base',themeVariables:{fontFamily:'arial,sans-serif',fontSize:'14px',primaryColor:'#ffffff',primaryBorderColor:'#28253D',primaryTextColor:'#28253D',lineColor:'#000000',clusterBkg:'#F9F9FB',clusterBorder:'#BDBCCC'},flowchart:{htmlLabels:true,useMaxWidth:false,wrappingWidth:120,nodeSpacing:50,rankSpacing:70,padding:16}});
const sections=[...src.matchAll(/subgraph (EOL_S\d+)\["([^"]+)"\]([\s\S]*?)\n    end/g)].map(m=>({id:m[1],title:m[2],body:m[3]}));
const definitions={},owner={},edges=[];
for(const s of sections){for(const m of s.body.matchAll(/\b(EOL_\w+)\["([^"]+)"\]/g)){definitions[m[1]]=m[2];owner[m[1]]=s.id;}for(const line of s.body.split('\n')){if(/-->|-\.->/.test(line)){const ids=[...line.matchAll(/\bEOL_\w+/g)].map(m=>m[0]);const label=line.match(/\|"([^"]+)"\|/);edges.push({from:ids[0],to:ids[1],label:label?.[1]||'',dashed:line.includes('-.->')});}}}
const palette=src.slice(src.indexOf('    classDef feed'));
let output=[];
for(const [index,s] of sections.entries()){
const ids=Object.keys(owner).filter(id=>owner[id]===s.id);
const local=edges.filter(e=>owner[e.from]===s.id&&owner[e.to]===s.id);
const styles=palette.split('\n').filter(l=>l.trim().startsWith('classDef ')).join('\n')+'\n'+palette.split('\n').filter(l=>l.trim().startsWith('class ')).map(l=>{const m=l.trim().match(/^class (\S+) (\w+)/);let keep=m[1].split(',').filter(id=>ids.includes(id));return keep.length?`class ${keep.join(',')} ${m[2]}`:''}).join('\n');
const code='flowchart TB\nsubgraph '+s.id+'["'+s.title+'"]\ndirection TB\n'+ids.map(id=>`${id}["${definitions[id]}"]`).join('\n')+'\n'+local.map(e=>`${e.from} ${e.dashed?'-.->':'-->'}${e.label?'|"'+e.label+'"|':''} ${e.to}`).join('\n')+'\nend\n'+styles;
const rendered=await mermaid.render('eol'+(index+1),code);const host=document.createElement('div');host.innerHTML=rendered.svg;document.body.append(host);const svg=host.querySelector('svg'),vb=svg.viewBox.baseVal;const coords={};
for(const el of svg.querySelectorAll('g.node')){const id=el.id.match(/flowchart-(EOL_\w+)-\d+/)?.[1];if(!id)continue;const b=el.getBBox(),m=el.getCTM(),inv=svg.getCTM().inverse();const p=new DOMPoint(b.x,b.y).matrixTransform(m).matrixTransform(inv);coords[id]={x:p.x,y:p.y,w:b.width,h:b.height};}
output.push({id:s.id,title:s.title,svg:rendered.svg,width:vb.width,height:vb.height,nodes:coords});host.remove();}
return {sections:output,edges:edges.filter(e=>owner[e.from]!==owner[e.to])};
},src);fs.writeFileSync(path.join(root,'output/eol-layout.json'),JSON.stringify(result));console.log('Rendered',result.sections.length,'EOL sections in source order;',result.edges.length,'cross-section connections.');}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
