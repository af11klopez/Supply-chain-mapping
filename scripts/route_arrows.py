"""Orthogonal margin routing around fixed node rectangles."""
import heapq,math

def simplify(points):
 out=[]
 for p in points:
  if out and p==out[-1]:continue
  if len(out)>1 and ((out[-2][0]==out[-1][0]==p[0]) or (out[-2][1]==out[-1][1]==p[1])):out[-1]=p
  else:out.append(p)
 return out

def route(start,end,rects,used):
 pad=10
 boxes=[(b['x']-pad,b['y']-pad,b['x']+b['w']+pad,b['y']+b['h']+pad) for b in rects]
 xs={start[0],end[0]};ys={start[1],end[1]}
 for l,t,r,b in boxes:xs.update([l,r]);ys.update([t,b])
 for a,b in used:
  if a[1]==b[1] and abs(a[1]-start[1])<400:ys.update([a[1]-16,a[1]+16])
 xs=sorted(xs);ys=sorted(ys)
 def clear(a,b):
  x1,y1=a;x2,y2=b
  if x1==x2:return not any(l<x1<r and max(min(y1,y2),t)<min(max(y1,y2),bt) for l,t,r,bt in boxes)
  return not any(t<y1<bt and max(min(x1,x2),l)<min(max(x1,x2),r) for l,t,r,bt in boxes)
 def reuse(a,b):
  cost=0
  for c,d in used:
   if a[0]==b[0]==c[0]==d[0]:cost+=max(0,min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1])))*8
   if a[1]==b[1]==c[1]==d[1]:cost+=max(0,min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0])))*8
  return cost
 si=(xs.index(start[0]),ys.index(start[1]),0);target=(xs.index(end[0]),ys.index(end[1]));queue=[(0,0,si)];dist={si:0};prev={};cache={}
 while queue:
  _,cost,state=heapq.heappop(queue)
  if cost!=dist[state]:continue
  ix,iy,direction=state
  if (ix,iy)==target:
   result=[]
   while state is not None:result.append((xs[state[0]],ys[state[1]]));state=prev.get(state)
   return simplify(result[::-1])
  a=(xs[ix],ys[iy])
  for j,k,nd in [(ix-1,iy,1),(ix+1,iy,1),(ix,iy-1,2),(ix,iy+1,2)]:
   if not(0<=j<len(xs) and 0<=k<len(ys)):continue
   b=(xs[j],ys[k]);key=tuple(sorted((a,b)))
   if key not in cache:cache[key]=clear(a,b)
   if not cache[key]:continue
   nc=cost+abs(a[0]-b[0])+abs(a[1]-b[1])+(28 if direction and nd!=direction else 0)+reuse(a,b)
   nxt=(j,k,nd)
   if nc<dist.get(nxt,math.inf):
    dist[nxt]=nc;prev[nxt]=state
    heapq.heappush(queue,(nc+abs(b[0]-end[0])+abs(b[1]-end[1]),nc,nxt))
 raise RuntimeError(f'No obstacle-free route: {start} → {end}')
