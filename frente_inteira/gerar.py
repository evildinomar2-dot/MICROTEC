"""Frente completa em peça única, com cinco vãos atravessantes; sem molduras.
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
HEIGHT=65.0    # cota frontal do desenho; detalhes de distribuição ainda aproximados
DEPTH=40.0     # hipótese: retorno lateral não está cotado
THICKNESS=2.0 # alvo aproximado de espessura; compensação discreta de rebaixos e frisos
# Coordenada normal horizontal externa, altura: perfil de frisos e saia.
profile=np.array([(0,2.6),(.6,3),(2.4,3),(3.3,2),(4.3,.6),(7,.25),(16,-.6),(27,-.1),(29,.5),(29.8,.45),(30.4,.1),(31.1,1.8),(31.8,2.5),(34.3,2.5),(35,1.4),(36,.2),(40,-.2),(62,-.2),(65,-.5)])
Z=np.linspace(0,HEIGHT,261)
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
# Área central para placa; proporção inferida do desenho.
sdf=sdf_rect(Y,ZZ,0,18.5,44,17,1.5)
base-=1.45*smoothstep(-sdf/1.0)
base+=.18*np.exp(-((sdf-.2)/.45)**2)
# Junções verticais discretas visíveis na referência, abaixo do friso superior.
for cy in (-48,48):
 base-=.25*np.exp(-((Y-cy)/.42)**2)*smoothstep((ZZ-4)/2)*smoothstep((29-ZZ)/2)

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
 # Nariz inclinado para trás acima do para-choque e ligeiro estreitamento.
 taper=smoothstep((ZZ-35)/30)
 xx += 11*taper*(1-path[:,0,None]/end)
 yy *= 1-.015*taper
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
# Vãos reais: cortadores atravessam toda a profundidade da peça.
def hole_prism(cy,cz,w,h,r):
 pts=[]
 for yc,zc,start in [(cy+w/2-r,cz+h/2-r,0),(cy-w/2+r,cz+h/2-r,90),(cy-w/2+r,cz-h/2+r,180),(cy+w/2-r,cz-h/2+r,270)]:
  for a in np.deg2rad(np.linspace(start,start+90,13)):
   pts.append([yc+r*np.cos(a),zc+r*np.sin(a)])
 nv=len(pts);v=[(x,y,z) for x in (-2,DEPTH+2) for y,z in pts];f=[]
 for j in range(1,nv-1):f.extend([[0,j,j+1],[nv,nv+j+1,nv+j]])
 for j in range(nv):
  k=(j+1)%nv;f.extend([[j,k,nv+k],[j,nv+k,nv+j]])
 m=tm.Trimesh(v,f);m.fix_normals();assert m.is_volume
 return m
holes=[
 {'nome':'grade_central','cy':0,'cz':48.5,'w':92,'h':23,'r':1.2},
 {'nome':'farois_esquerda','cy':-80,'cz':51,'w':52,'h':16,'r':1.1},
 {'nome':'farois_direita','cy':80,'cz':51,'w':52,'h':16,'r':1.1},
 {'nome':'entrada_inferior_esquerda','cy':-79,'cz':21.5,'w':50,'h':11,'r':1.4},
 {'nome':'entrada_inferior_direita','cy':79,'cz':21.5,'w':50,'h':11,'r':1.4},
]
cutters=[hole_prism(**{k:v for k,v in h.items() if k!='nome'}) for h in holes]
mesh=tm.boolean.difference([mesh,*cutters],engine='manifold')
mesh.remove_unreferenced_vertices();mesh.fix_normals()
assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1
# Cinco túneis numa peça única => característica de Euler 2-2*5=-8.
assert mesh.euler_number==-8,mesh.euler_number
mesh.export(ROOT/'frente_inteira.stl')
mesh=tm.load_mesh(ROOT/'frente_inteira.stl')
assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1
assert np.allclose(mesh.extents,[DEPTH,WIDTH,HEIGHT],atol=.002)
ray_checks=[]
for h in holes:
 origins=np.array([[-1,y,z] for y in np.linspace(h['cy']-.4*h['w'],h['cy']+.4*h['w'],7) for z in np.linspace(h['cz']-.4*h['h'],h['cz']+.4*h['h'],7)])
 blocked=mesh.ray.intersects_any(origins,np.tile([1.,0,0],(len(origins),1)))
 assert not blocked.any(),h['nome']
 ray_checks.append({'abertura':h['nome'],'raios_testados':len(origins),'bloqueados':int(blocked.sum())})
# Controles: faixa do para-choque, placa, pontes entre grade e faróis e borda superior.
controls=np.array([[-1,0,33],[-1,0,18],[-1,50,51],[-1,-50,51],[-1,0,63]])
assert mesh.ray.intersects_any(controls,np.tile([1.,0,0],(len(controls),1))).all()
validation={'descricao':'frente completa em uma peça, cinco vãos reais, sem molduras ou insertos','arquivo':'frente_inteira.stl','dimensoes_XYZ_mm':mesh.extents.round(3).tolist(),'volume_mm3':round(mesh.volume,3),'componentes':len(mesh.split()),'malha_fechada':bool(mesh.is_watertight),'caracteristica_euler':int(mesh.euler_number),'vazios':holes,'raios_aberturas':ray_checks,'controles_material_solido':5,'espessura_alvo_aproximado_mm':THICKNESS,'verificacao_parede_antes_dos_cortes':thickness_check,'simplificacao_tolerancia_mm':.015,'impressao_fisica_validada':False}
(ROOT/'validacao.json').write_text(json.dumps(validation,indent=2))

# Todas as imagens abaixo são projeções dos STL, sem preenchimento dos vãos.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
light=np.array([-1,-.4,1.5]);light/=np.linalg.norm(light)

def render(ax,eye):
 eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
 right=np.array([0,-1.,0]) if abs(eye[2])>.9999 else np.cross([0,0,1],eye)
 right/=np.linalg.norm(right);up=np.cross(eye,right)
 vis=mesh.face_normals@eye>1e-7
 faces=mesh.faces[vis];normal=mesh.face_normals[vis];v=mesh.vertices
 proj=np.column_stack([v@right,v@up]);depth=(v@eye)[faces].mean(axis=1)
 intensity=.35+.65*np.clip(normal@light,0,1)
 colors=np.clip(intensity[:,None]*np.array(to_rgb('#b6c0cc')),0,1)
 order=np.argsort(depth)
 ax.add_collection(PolyCollection(proj[faces][order],facecolors=colors[order],edgecolors='none',antialiaseds=False))
 ax.autoscale_view();ax.margins(.055);ax.set_aspect('equal');ax.axis('off');ax.set_facecolor('#ffffff')

fig,axs=plt.subplots(2,2,figsize=(16,10),facecolor='#ffffff')
for ax,eye,title in zip(axs.flat,[[-1,-.65,.6],[-1,0,0],[1,.6,.5],[0,-1,0]],['Frente completa • peça única','Frontal • cinco aberturas livres','Vista por trás • casca aberta','Perfil • retorno lateral']):
 render(ax,eye);ax.set_title(title,fontsize=15,pad=15)
fig.suptitle('BUICK REGAL — FRENTE INTEIRA COM VÃOS',fontsize=22,fontweight='bold',y=.96)
fig.text(.5,.025,'240 mm de largura × 65 mm de altura • retorno de 40 mm estimado\nUm vão de grade, dois vãos para conjuntos de faróis e duas entradas inferiores • molduras ficam para depois',ha='center',fontsize=12)
fig.subplots_adjust(left=.04,right=.96,bottom=.13,top=.87,hspace=.36,wspace=.16)
fig.savefig(ROOT/'previa_frente_inteira.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(14,7),facecolor='#ffffff');render(ax,[-1,-.65,.5])
ax.set_title('Frente inteira • sem grade, sem faróis e sem molduras',fontsize=18,pad=20)
fig.tight_layout();fig.savefig(ROOT/'perspectiva.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(14,6),facecolor='#ffffff');render(ax,[-1,0,0])
ax.annotate('',xy=(-120,-7),xytext=(120,-7),arrowprops=dict(arrowstyle='<->',color='#263544',lw=1.2))
ax.text(0,-10,'240 mm',ha='center',va='top',fontsize=13)
ax.annotate('',xy=(130,0),xytext=(130,65),arrowprops=dict(arrowstyle='<->',color='#263544',lw=1.2))
ax.text(134,32.5,'65 mm',ha='left',va='center',fontsize=12)
ax.set_xlim(-127,155);ax.set_ylim(-18,72)
ax.set_title('Vista frontal — as áreas vazias atravessam a casca',fontsize=18,pad=15)
fig.tight_layout();fig.savefig(ROOT/'frontal.png',dpi=170);plt.close(fig)
print(json.dumps(validation,indent=2))
