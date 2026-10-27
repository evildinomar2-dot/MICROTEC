"""Estudo paramétrico V2 em mm. Frente X=0, solo Z=0. Não é CAD de fábrica."""
from pathlib import Path
import json, zipfile
import numpy as np
import trimesh as tm
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).parent
STL=ROOT/'stl';STL.mkdir(exist_ok=True)

def box(a,b):
 a,b=np.array(a),np.array(b);m=tm.creation.box(b-a);m.apply_translation((a+b)/2);return m

def boolean(op,meshes):
 return getattr(tm.boolean,op)(meshes,engine='manifold')
def sub(a,*b):return boolean('difference',[a,*b])
def union(*m):return boolean('union',list(m))
def intersect(a,b):return boolean('intersection',[a,b])
def prism(poly,y0,y1):
 n=len(poly);v=[(x,y,z) for y in (y0,y1) for x,z in poly];f=[]
 for j in range(1,n-1):f.extend([[0,j,j+1],[n,n+j+1,n+j]])
 for j in range(n):
  k=(j+1)%n;f.extend([[j,k,n+k],[j,n+k,n+j]])
 m=tm.Trimesh(v,f);m.fix_normals();return m

def curve(points):return PchipInterpolator(*np.array(points).T)
WIDTH=curve([(0,112),(22,117),(120,118),(205,115),(350,115),(430,116),(520,118),(598,116),(620,112)])
TOP=curve([(0,66),(22,71),(120,78),(205,82),(270,147),(285,153),(385,153),(400,148),(480,80),(598,72),(620,66)])
EDGE=curve([(0,102),(22,105),(120,105),(205,102),(270,92),(285,91),(385,92),(400,94),(480,105),(598,104),(620,102)])
BELT=curve([(0,62),(22,69),(120,76),(205,80),(270,82),(385,82),(480,77),(520,75),(598,69),(620,62)])
XS=np.unique(np.r_[np.arange(0,621,4),[22,120,205,270,285,330,385,400,410,480,520,598,620]])

def shell_solid(inner=False):
 verts=[];xs=XS.copy().astype(float)
 if inner:xs=xs[(xs>5)&(xs<615)];xs=np.r_[5,xs,615]
 for x in xs:
  w=float(WIDTH(x));t=float(TOP(x));r=float(EDGE(x));s=float(BELT(x))
  # Ombros elevados sobre as rodas, com transição suave longitudinal.
  bump=sum(7*np.exp(-((x-a)/49)**4) for a in (120,520))
  s+=bump
  t+=3*sum(np.exp(-((x-a)/49)**4) for a in (120,520))
  if inner:w-=2;r-=2;s-=2;t-=2
  bottom=-4 if inner else 8
  half=[(0,bottom),(w-5,bottom),(w-3,17),(w-1.2,23),(w-1,29),(w-.8,31),(w,35),(w,45),(w-.2,s-7),(w-1,s-3),(w-3,s),(w-6,s+1),(r+2,t-.5),(r,t)]
  # Coroa do capô/teto; evita as placas planas da V1.
  half += [(r*u,t+2*(1-u*u)) for u in np.linspace(.9,0,10)]
  yz=half + [(-y,z) for y,z in half[-2:0:-1]]
  for y,z in yz:
   # Relevo da borda dos para-lamas, integrado à própria casca.
   rho=min(np.hypot(x-a,z-33) for a in (120,520))
   flare=2.4*np.exp(-((rho-52)/8)**2)*(abs(y)/max(w,1))**8
   verts.append([x,y+np.sign(y)*flare,z])
 n=len(yz);f=[]
 for k in range(len(xs)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n
   f.extend([[a,b,b+n],[a,b+n,a+n]])
 # End sections are non-convex: triangulate using earcut.
 import mapbox_earcut
 for k in (0,len(xs)-1):
  pts=np.array(verts[k*n:(k+1)*n])[:,1:].astype(np.float64)
  tri=mapbox_earcut.triangulate_float64(pts,np.array([n],dtype=np.uint32)).reshape(-1,3)
  f.extend((tri+k*n).tolist())
 m=tm.Trimesh(verts,f);m.fix_normals();assert m.is_volume
 return m

print('Construindo casca...',flush=True)
body=sub(shell_solid(),shell_solid(True))
# Vãos para rodas, não rodas inclusas. 400 mm entre centros.
for x in (120,520):
 for y in (-124,124):
  c=tm.creation.cylinder(radius=46,height=48,sections=144)
  c.apply_transform(tm.transformations.rotation_matrix(np.pi/2,[1,0,0]));c.apply_translation([x,y,33]);body=sub(body,c)
for y0,y1 in ((85,132),(-132,-85)):
 for poly in ([(221,94),(278,141),(344,141),(344,94)],[(356,94),(356,141),(384,141),(446,94)]):
  body=sub(body,prism(poly,y0,y1))
body=sub(body,prism([(202,94),(253,141),(281,141),(230,94)],-76,76))
body=sub(body,prism([(396,140),(424,140),(480,93),(452,93)],-76,76))
# Largura máxima real de 240 mm, após remover as passagens das rodas.
body.apply_scale([1,240/body.extents[1],1])
# Grade central e quatro faróis: alojamentos profundos em placa frontal de 5 mm.
body=sub(body,box([-1,-48,31],[3.2,48,61]))
for lo,hi in [(-104,-79),(-76,-51),(51,76),(79,104)]:
 body=sub(body,box([-1,lo,38],[3.2,hi,59]))
# Frisos de para-choque e entradas baixas, sem atravessar a parede restante.
body=sub(body,box([-1,-108,24],[1.5,108,27]))
for lo,hi in [(-98,-43),(43,98)]:body=sub(body,box([-1,lo,12],[2.2,hi,21]))
# Alojamentos de lanternas e placa traseira.
for lo,hi in [(-103,-29),(29,103)]:body=sub(body,box([616.8,lo,41],[621,hi,59]))
body=sub(body,box([618,-24,32],[621,24,56]),box([618.5,-107,25],[621,107,28]))
print('Dividindo painéis...',flush=True)
parts={};remaining=body
# Cortes com vãos de janela fora das linhas de separação do teto.
regions=[('01_frente',([-1,-130,0],[22,130,160])),('02_traseira',([598,-130,0],[621,130,160])),('03_capo',([22,-96,0],[205,96,160])),('04_tampa_porta_malas',([480,-96,0],[598,96,160])),('05_cabine_frente',([205,-130,88],[330,130,160])),('06_cabine_traseira',([330,-130,88],[480,130,160]))]
for name,(a,b) in regions:
 cutter=box(a,b);parts[name]=intersect(remaining,cutter);remaining=sub(remaining,cutter)
for side,lo,hi in [('esquerdo',-130,0),('direito',0,130)]:
 for name,x0,x1 in [('para_lama_dianteiro',22,205),('porta',205,410),('lateral_traseira',410,598)]:
  parts[name+'_'+side]=intersect(remaining,box([x0,lo,0],[x1,hi,160]))
# Metades das faces facilitam impressão sem presumir uma impressora de 240 mm.
for name in ['01_frente','02_traseira']:
 p=parts.pop(name)
 for side,lo,hi in [('esquerda',-130,0),('direita',0,130)]:parts[name+'_'+side]=intersect(p,box([-2,lo,0],[622,hi,160]))
# Inserto de grade com fundo, aro e aletas. Profundidade inclui 0,2 mm de folga.
grille=box([1.7,-47.7,31.3],[3,47.7,60.7])
bars=[grille]
for y in np.arange(-45,46,4):bars.append(box([.2,y-.65,32],[2,y+.65,60]))
for z in (32,59):bars.append(box([.2,-47,z],[2,47,z+1]))
parts['07_grade']=union(*bars)
# Lentes opacas demonstrativas com moldura e cruz em relevo; sem transparência no STL.
for i,(lo,hi) in enumerate([(-104,-79),(-76,-51),(51,76),(79,104)],1):
 p=box([1.5,lo+.3,38.3],[3,hi-.3,58.7])
 bars=[p,box([.4,lo+.8,38.8],[2,hi-.8,40]),box([.4,lo+.8,57],[2,hi-.8,58.2]),box([.4,lo+.8,39],[2,lo+2,58]),box([.4,hi-2,39],[2,hi-.8,58]),box([1,(lo+hi)/2-.5,40],[2,(lo+hi)/2+.5,57]),box([1,lo+2,48],[2,hi-2,49])]
 parts[f'farol_{i}']=union(*bars)
for side,lo,hi in [('esquerda',-103,-29),('direita',29,103)]:
 p=box([617,lo+.3,41.3],[618.5,hi-.3,58.7]);bars=[p]
 for y in np.arange(lo+8,hi-2,12):bars.append(box([618, y,42],[619.5,y+1,58]))
 bars.append(box([618,lo+.5,49],[619.5,hi-.5,50]));parts['lanterna_'+side]=union(*bars)
parts['spoiler']=prism([(582,76),(585,76),(594,94),(591,94)],-104,104)
# Placas de união genéricas independentes, para colagem interna somente após ajuste.
# Não são fixações do chassi nem encaixes dimensionados para a impressora.
parts['tala_colagem_reta']=box([0,0,0],[24,12,2])
assembly=[];report=[];discarded=[]
for name,m in parts.items():
 m.remove_unreferenced_vertices();m.fix_normals()
 chunks=sorted(m.split(only_watertight=False),key=lambda c:-c.volume)
 for i,c in enumerate(chunks):
  if c.volume<10:
   discarded.append({'origem':name,'volume_mm3':float(c.volume)});continue
  key=name if len(chunks)==1 else f'{name}_{i+1}'
  assert c.is_watertight and c.is_volume,key
  c.export(STL/(key+'.stl'))
  report.append({'peca':key,'dimensoes_mm':np.round(c.extents,3).tolist(),'volume_mm3':round(c.volume,3),'malha_fechada':True})
  if name!='tala_colagem_reta':assembly.append((key,c))
# Remove apenas saídas antigas deste gerador que não constam do novo manifesto.
expected={r['peca']+'.stl' for r in report}
for f in STL.glob('*.stl'):
 if f.name not in expected:f.unlink()
combined=tm.util.concatenate([m for _,m in assembly]);combined.export(ROOT/'montagem_referencia.stl')
validation={'versao':2,'unidade':'mm','dimensoes_conjunto_mm':combined.extents.tolist(),'entre_eixos_mm':400,'z_solo_mm':0,'z_base_mm':8,'z_teto_mm':155,'espessura':'deslocamento nominal de 2 mm; varia nas inclinações','pecas':report,'fragmentos_descartados':discarded}
(ROOT/'validacao.json').write_text(json.dumps(validation,indent=2))
print('Gerando vistas...',flush=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
fig,axs=plt.subplots(2,2,figsize=(16,10),facecolor='#e9edf1')
light=np.array([-1,-.5,1.5]);light/=np.linalg.norm(light)
for ax,view in zip(axs.flat,['perspectiva','explodida','lateral','frente']):
 ax.set_facecolor('#e9edf1')
 eye=np.array({'perspectiva':[-1,-1.5,.9],'explodida':[-1,-1.5,.9],'lateral':[0,-1,0],'frente':[-1,0,.10]}[view],dtype=float);eye/=np.linalg.norm(eye)
 right=np.cross([0,0,1],eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
 polygons=[];shades=[];depths=[]
 for i,(name,m) in enumerate(assembly):
  v=m.vertices.copy();color='#b5beca'
  if 'grade' in name:color='#343b45'
  elif 'farol' in name:color='#e0e8f0'
  elif 'lanterna' in name:color='#9f2835'
  elif 'spoiler' in name:color='#636e7e'
  if view=='explodida':
   color=plt.cm.tab20(i/max(len(assembly)-1,1))[:3]
   v[:,0]+=(m.centroid[0]-310)*.20
   v[:,1]+=np.sign(m.centroid[1])*28
   if any(s in name for s in ('cabine','capo','tampa')):v[:,2]+=38
  visible=m.face_normals@eye>1e-7
  faces=m.faces[visible];normals=m.face_normals[visible]
  proj=np.column_stack([v@right,v@up]);polygons.extend(proj[faces])
  depths.extend((v@eye)[faces].mean(axis=1))
  intensity=.45+.55*np.clip(normals@light,0,1)
  shades.extend(np.clip(intensity[:,None]*np.array(to_rgb(color))[None,:],0,1))
 order=np.argsort(depths);polygons=np.array(polygons);shades=np.array(shades)
 ax.add_collection(PolyCollection(polygons[order],facecolors=shades[order],edgecolors='none',antialiaseds=False))
 ax.autoscale_view();ax.margins(.06);ax.set_aspect('equal');ax.axis('off')
 ax.set_title({'perspectiva':'V2 • geometria montada','explodida':'Divisão em peças','lateral':'Perfil lateral • sem rodas','frente':'Frente • grade e quatro faróis'}[view],fontsize=16,pad=14)
fig.suptitle('BUICK REGAL NASCAR 1987 — ESTUDO RC V2',fontsize=22,fontweight='bold',y=.97)
fig.text(.5,.025,'620 × 240 mm • entre-eixos 400 mm • teto na cota 155 mm\nPrévia das malhas reais | interpretação aproximada | encaixe no chassi ainda não validado',ha='center',fontsize=12)
fig.subplots_adjust(left=.03,right=.97,bottom=.12,top=.88,wspace=.10,hspace=.32)
fig.savefig(ROOT/'previa_v2.png',dpi=160);plt.close(fig)
print('Concluído:',len(report),'STL; fragmentos descartados:',len(discarded),flush=True)
