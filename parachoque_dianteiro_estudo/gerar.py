"""Estudo isolado do para-choque/saia inferior a partir da referência visual.
Unidades mm. Frente X=0; largura em Y; altura em Z.
Cotas confirmadas: apenas largura total de referência, 240 mm.
"""
from pathlib import Path
import json
import numpy as np
import trimesh as tm
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).parent
WIDTH=240.0
HEIGHT=44.0    # hipótese visual: não foi medida no carro
DEPTH=40.0     # hipótese: retorno lateral não está cotado
THICKNESS=2.0 # alvo aproximado de espessura; compensação discreta de rebaixos e frisos
# Coordenada normal horizontal externa, altura: perfil de frisos e saia.
profile=np.array([(0,2.6),(0.6,3),(2.4,3),(3.3,2),(4.3,.6),(7,.25),(17,-.6),(31,-.1),(35,.5),(35.8,.45),(36.4,.10),(37.1,1.8),(37.8,2.5),(42.8,2.5),(43.5,2),(44,1.0)])
Z=np.linspace(0,HEIGHT,177)
section=PchipInterpolator(profile[:,0],profile[:,1])
# Trajeto em U: frente quase plana, curva curta nos cantos, retorno lateral.
front_y=np.linspace(0,106,213)
front_x=.8+1.4*(front_y/106)**4
slope=5.6/106*(front_y/106)**3
nx=-1/np.sqrt(1+slope*slope);ny=slope/np.sqrt(1+slope*slope)
right=[[x,y,a,b] for x,y,a,b in zip(front_x,front_y,nx,ny)]
for ang in np.linspace(0,np.pi/2,49)[1:]:
 right.append([13.2-11*np.cos(ang),106+11*np.sin(ang),-np.cos(ang),np.sin(ang)])
# Min X outermost lip is -2.2, translated to zero below.
end=DEPTH-2.2
for x in np.linspace(13.2,end,31)[1:]:right.append([x,117,0,1])
left=[[x,-y,nx,-ny] for x,y,nx,ny in right[:0:-1]]
path=np.array(left+right)
# Amostragem uniforme em comprimento do trajeto, usada na compensação interna.
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path[:,:2],axis=0),axis=1))]
samples=np.linspace(0,arc[-1],2*int(np.ceil(arc[-1]))+1)
path=np.column_stack([np.interp(samples,arc,path[:,k]) for k in range(4)])
path[:,2:]/=np.linalg.norm(path[:,2:],axis=1)[:,None]
Y=path[:,1,None];ZZ=Z[None,:]
base=np.broadcast_to(section(Z),(len(path),len(Z))).copy()

def sdf_rect(y,z,cy,cz,w,h,r):
 qy=np.abs(y-cy)-(w/2-r);qz=np.abs(z-cz)-(h/2-r)
 return np.minimum(np.maximum(qy,qz),0)+np.sqrt(np.maximum(qy,0)**2+np.maximum(qz,0)**2)-r

def smoothstep(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
# Entradas de ar representadas como rebaixos fechados: não são furos de ventilação.
for cy in (-79,79):
 sdf=sdf_rect(Y,ZZ,cy,26,52,12,1.7)
 base-=3.6*smoothstep(-sdf/1.3)
 base+=.50*np.exp(-((sdf-.35)/.48)**2)
# Área central para placa; proporção inferida do desenho.
sdf=sdf_rect(Y,ZZ,0,22.5,44,19,1.5)
base-=1.45*smoothstep(-sdf/1.0)
base+=.18*np.exp(-((sdf-.2)/.45)**2)
# Junções verticais discretas visíveis na referência, abaixo do friso superior.
for cy in (-48,48):
 base-=.25*np.exp(-((Y-cy)/.42)**2)*smoothstep((ZZ-4)/2)*smoothstep((35-ZZ)/2)

# Offset interno por envelope circular no plano do trajeto x altura.
# Mais material sob as paredes inclinadas dos rebaixos, evitando simplesmente
# deslocar 2 mm horizontalmente, o que produziria paredes muito finas.
ds=samples[1]-samples[0];dz=Z[1]-Z[0]
ns=int(np.ceil(THICKNESS/ds));nz=int(np.ceil(THICKNESS/dz))
padded=np.pad(base,((ns,ns),(nz,nz)),mode='edge')
inner=np.full_like(base,np.inf)
for i in range(-ns,ns+1):
 for j in range(-nz,nz+1):
  r2=(i*ds)**2+(j*dz)**2
  if r2>THICKNESS**2:continue
  shifted=padded[ns+i:ns+i+len(path),nz+j:nz+j+len(Z)]
  inner=np.minimum(inner,shifted-np.sqrt(THICKNESS**2-r2))
verts=[]
for d in (base,inner):
 xx=path[:,0,None]+path[:,2,None]*d
 yy=path[:,1,None]+path[:,3,None]*d
 zz=np.broadcast_to(ZZ,xx.shape)
 verts.extend(np.stack([xx,yy,zz],axis=-1).reshape(-1,3))
nu,nv=len(path),len(Z);n=nu*nv
faces=[]
for layer in (0,n):
 for i in range(nu-1):
  for j in range(nv-1):
   a=layer+i*nv+j;b=a+nv
   faces.extend([[a,b,b+1],[a,b+1,a+1]])
# Fechar espessura ao longo das quatro bordas da superfície em U.
boundary=list(range(nv))+[i*nv+nv-1 for i in range(1,nu)]+list(range((nu-1)*nv+nv-2,(nu-1)*nv-1,-1))+[i*nv for i in range(nu-2,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([[a,b,b+n],[a,b+n,a+n]])
# Distância da superfície interna para a externa em 3.000 amostras
# determinísticas. Não equivale a certificação de espessura mínima global.
outer_surface=tm.Trimesh(np.array(verts)[:n],faces[:2*(nu-1)*(nv-1)],process=False)
inner_points=np.array(verts)[n:]
idx=np.linspace(0,len(inner_points)-1,3000,dtype=int)
_,distances,_=tm.proximity.closest_point(outer_surface,inner_points[idx])
thickness_check={'amostras':len(idx),'distancia_min_mm':round(float(distances.min()),4),'distancia_mediana_mm':round(float(np.median(distances)),4),'metodo':'distancia de vertices internos amostrados à superfície externa; não é garantia global'}
assert distances.min()>1.65,thickness_check
mesh=tm.Trimesh(verts,faces);mesh.fix_normals()
# Reduzir o peso dos STL, com tolerância geométrica explícita de 0,015 mm.
import manifold3d as md
solid=md.Manifold(md.Mesh(vert_properties=mesh.vertices.astype(np.float32),tri_verts=mesh.faces.astype(np.uint32)))
reduced=solid.simplify(.015).to_mesh()
mesh=tm.Trimesh(reduced.vert_properties[:,:3],reduced.tri_verts)
mesh.fix_normals()
mesh.apply_translation([-mesh.bounds[0,0],0,0])
assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1
assert np.allclose(mesh.extents,[DEPTH,WIDTH,HEIGHT],atol=.001),mesh.extents
mesh.export(ROOT/'parachoque_inteiro.stl')
# Duas metades opcionais. A peça inteira permanece como referência principal.
parts={}
for name,y0,y1 in [('metade_esquerda',-121,0),('metade_direita',0,121)]:
 bounds=np.array([[-1,y0,-1],[DEPTH+1,y1,HEIGHT+1]])
 cutter=tm.creation.box(bounds[1]-bounds[0]);cutter.apply_translation(bounds.mean(axis=0))
 m=tm.boolean.intersection([mesh,cutter],engine='manifold')
 assert m.is_watertight and m.is_volume and len(m.split())==1
 m.export(ROOT/(name+'.stl'));parts[name]=m
assert abs(sum(m.volume for m in parts.values())-mesh.volume)<.05
# Reabrir os STL para validar a entrega, não apenas a malha em memória.
checks=[]
for name in ['parachoque_inteiro',*parts]:
 m=tm.load_mesh(ROOT/(name+'.stl'))
 assert m.is_watertight and m.is_volume and len(m.split())==1
 checks.append({'arquivo':name+'.stl','dimensoes_XYZ_mm':m.extents.round(3).tolist(),'volume_mm3':round(m.volume,3),'fechado':True,'componentes':1})
(ROOT/'validacao.json').write_text(json.dumps({'descricao':'estudo visual isolado, sem validação de impressão ou encaixes','largura_referencia_mm':WIDTH,'altura_assumida_mm':HEIGHT,'profundidade_assumida_mm':DEPTH,'espessura_alvo_aproximado_mm':THICKNESS,'entradas_laterais_mm':[52,12],'placa_rebaixo_mm':[44,19],'simplificacao_tolerancia_mm':.015,'verificacao_parede':thickness_check,'stl':checks},indent=2))

# Renderizações ortográficas das malhas reais, com sombras projetadas por raios.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
light=np.array([-1,-.35,1.6]);light/=np.linalg.norm(light)
# As faces das zonas rebaixadas são cinza-escuro apenas para leitura visual;
# exporta-se também uma perspectiva monocromática, sem sugerir peças coloridas.
centers=mesh.triangles_center
C=centers[:,1];H=centers[:,2]
intake=np.zeros(len(centers),dtype=bool)
for cy in (-79,79):intake |= sdf_rect(C,H,cy,26,52,12,1.7)<-1.3
# A cor representa uma opção de pintura e não está contida no STL.

def render(ax,eye,marked=False):
 eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
 right=np.array([0,-1.,0]) if abs(eye[2])>.9999 else np.cross([0,0,1],eye)
 right/=np.linalg.norm(right);up=np.cross(eye,right)
 vis=mesh.face_normals@eye>1e-7
 faces=mesh.faces[vis];normal=mesh.face_normals[vis]
 v=mesh.vertices
 proj=np.column_stack([v@right,v@up]);depth=(v@eye)[faces].mean(axis=1)
 # Sem inventar reflexos: sombreamento difuso e realce das superfícies inclinadas.
 intensity=.28+.72*np.clip(normal@light,0,1)
 color=np.tile(to_rgb('#bfc7d0'),(len(faces),1))
 if marked:color[intake[vis]]=to_rgb('#444e59')
 colors=np.clip(intensity[:,None]*color,0,1)
 order=np.argsort(depth)
 ax.add_collection(PolyCollection(proj[faces][order],facecolors=colors[order],edgecolors='none',antialiaseds=False))
 ax.autoscale_view();ax.margins(.055);ax.set_aspect('equal');ax.axis('off');ax.set_facecolor('#edf0f4')

fig,axs=plt.subplots(2,2,figsize=(16,10),facecolor='#edf0f4')
for ax,eye,title,marked in zip(axs.flat,[[-1,-.8,.75],[-1,0,0],[0,0,1],[0,-1,0]],['Perspectiva • geometria sem pintura','Frente • rebaixos destacados em cinza','Vista superior • retorno dos cantos','Perfil lateral'],[False,True,False,False]):
 render(ax,eye,marked);ax.set_title(title,fontsize=15,pad=15)
fig.suptitle('BUICK REGAL — ESTUDO DO PARA-CHOQUE DIANTEIRO',fontsize=21,fontweight='bold',y=.96)
fig.text(.5,.025,'Somente o conjunto abaixo dos faróis • largura 240 mm\nAltura 44 mm e profundidade 40 mm são hipóteses | não validado para impressão ou montagem',ha='center',fontsize=12)
fig.subplots_adjust(left=.04,right=.96,bottom=.12,top=.87,hspace=.36,wspace=.2)
fig.savefig(ROOT/'previa_parachoque.png',dpi=160);plt.close(fig)
# Perspectiva grande sem cores por característica, para julgar a forma.
fig,ax=plt.subplots(figsize=(14,7),facecolor='#edf0f4');render(ax,[-1,-.7,.6],False)
ax.set_title('Para-choque dianteiro • estudo isolado',fontsize=20,pad=18)
fig.tight_layout();fig.savefig(ROOT/'perspectiva.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(14,5),facecolor='#edf0f4');render(ax,[-1,0,0],True)
ax.annotate('',xy=(-120,-7),xytext=(120,-7),arrowprops=dict(arrowstyle='<->',color='#263544',lw=1.2))
ax.text(0,-10,'240 mm • largura de referência',ha='center',va='top',fontsize=13)
ax.annotate('',xy=(131,0),xytext=(131,44),arrowprops=dict(arrowstyle='<->',color='#263544',lw=1.2))
ax.text(135,22,'44 mm\nhipótese',ha='left',va='center',fontsize=12)
ax.set_xlim(-127,157);ax.set_ylim(-18,52)
ax.set_title('Frente — conferir proporções antes de imprimir',fontsize=18,pad=15)
fig.tight_layout();fig.savefig(ROOT/'frente_medidas.png',dpi=160);plt.close(fig)
print(json.dumps({'arquivos':checks,'parede':thickness_check},indent=2))
