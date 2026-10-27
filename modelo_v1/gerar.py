"""Buick Regal NASCAR inspirado no esboço; unidades mm; frente x=0."""
from pathlib import Path
import json, zipfile
import numpy as np
import trimesh as tm
OUT=Path(__file__).parent
STL=OUT/'stl'; STL.mkdir(exist_ok=True)
# x, meia largura maxima, meia largura topo, altura ombro, altura topo
SECTIONS=[(0,110,100,60,65),(18,117,105,71,77),(120,120,106,78,84),(190,117,101,82,88),(260,116,88,84,155),(395,117,89,84,155),(480,119,104,76,86),(602,115,103,66,76),(620,110,100,59,65)]
def loft(inner=False):
    verts=[]
    for x,w,r,s,t in SECTIONS:
        if inner:
            w-=2; r-=2; s-=2; t-=2
            if x==0: x=2
            if x==620: x=618
        b=-5 if inner else 8
        verts.extend([(x,y,z) for y,z in [(-w,b),(-w,s-8),(-w+4,s),(-r,t-2),(-r+8,t),(r-8,t),(r,t-2),(w-4,s),(w,s-8),(w,b)]])
    faces=[]; n=10
    for k in range(len(SECTIONS)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=b+n;d=a+n
            faces.extend([[a,b,c],[a,c,d]])
    for k in (0,len(SECTIONS)-1):
        for j in range(1,n-1): faces.append([k*n,k*n+j,k*n+j+1])
    m=tm.Trimesh(verts,faces); m.fix_normals();return m

def box(bounds):
    a,b=np.array(bounds);m=tm.creation.box(b-a);m.apply_translation((a+b)/2);return m

def prism_xz(poly,y0,y1):
    v=[(x,y,z) for y in (y0,y1) for x,z in poly];n=len(poly);f=[]
    for j in range(1,n-1):f.extend([[0,j,j+1],[n,n+j+1,n+j]])
    for j in range(n):
        k=(j+1)%n;f.extend([[j,k,n+k],[j,n+k,n+j]])
    m=tm.Trimesh(v,f);m.fix_normals();return m

def diff(a,*b):return tm.boolean.difference([a,*b],engine='manifold')
def inter(a,b):return tm.boolean.intersection([a,b],engine='manifold')
body=diff(loft(),loft(True))
# Passagens de roda: diametro 92, centros longitudinais separados 400 mm.
for x in (120,520):
    for y in (-118,118):
        c=tm.creation.cylinder(radius=46,height=50,sections=96)
        c.apply_transform(tm.transformations.rotation_matrix(np.pi/2,[1,0,0]));c.apply_translation([x,y,34])
        body=diff(body,c)
# Janelas laterais abertas, com coluna B e janela traseira separada.
for y0,y1 in ((72,130),(-130,-72)):
    for poly in ([(210,94),(268,145),(347,145),(347,94)],[(359,94),(359,145),(389,145),(452,94)]):
        body=diff(body,prism_xz(poly,y0,y1))
# Para-brisa e vidro traseiro: abertura central deixa molduras.
body=diff(body,prism_xz([(190,96),(240,144),(262,144),(212,96)],-76,76))
body=diff(body,prism_xz([(395,144),(422,144),(481,96),(454,96)],-76,76))
# Rebaixos da grade e farois no painel dianteiro (relevos simplificados).
# O painel frontal e uma casca de 2 mm; detalhes ficam para V2.
# Sulcos rasos na face frontal, mantendo pelo menos 1 mm de material.
for ya,yb in [(-95,-70),(-67,-42),(42,67),(70,95)]:
    body=diff(body,box([(-1,ya,40),(0.8,yb,56)]))
for y in range(-34,35,4):
    body=diff(body,box([(-1,y,32),(0.8,y+1.5,59)]))
for ya,yb in [(-98,-28),(28,98)]:
    body=diff(body,box([(619.2,ya,43),(621,yb,55)]))
body.apply_scale([1,240/body.extents[1],1])
parts={}
remaining=body
regions=[('01_para_choque_dianteiro',[(0,-130,0),(18,130,170)]),('02_para_choque_traseiro',[(602,-130,0),(620,130,170)]),('03_capo',[(18,-95,0),(190,95,170)]),('04_porta_malas',[(480,-95,0),(602,95,170)]),('05_teto',[(190,-130,147),(480,130,160)]),('06_moldura_para_brisa',[(190,-95,0),(267,95,147)]),('07_moldura_vidro_traseiro',[(395,-95,0),(480,95,147)])]
for name,bounds in regions:
    cutter=box(bounds);p=inter(remaining,cutter)
    if len(p.faces):parts[name]=p
    remaining=diff(remaining,cutter)
for side,lo,hi in [('esquerdo',-130,0),('direito',0,130)]:
    for label,x0,x1 in [('para_lama_dianteiro',18,195),('porta_e_colunas',195,410),('lateral_traseira',410,602)]:
        p=inter(remaining,box([(x0,lo,0),(x1,hi,160)]))
        if len(p.faces):parts[label+'_'+side]=p
# Spoiler separado, lâmina de 2 mm; apenas encostado na tampa nesta V1.
parts['spoiler']=prism_xz([(587,77),(589,77),(595,94),(593,94)],-104,104)
report=[]
assembly=[]
for name,p in parts.items():
    p.remove_unreferenced_vertices();p.fix_normals()
    # Componentes desconectados são exportados individualmente.
    chunks=[c for c in p.split(only_watertight=False) if c.volume>=50]
    for i,m in enumerate(chunks):
        if m.volume<0.01:continue
        key=name if len(chunks)==1 else f'{name}_{i+1}'
        assert m.is_watertight and m.is_volume, key
        assembly.append((key,m))
        m.export(STL/(key+'.stl'))
        report.append({'peca':key,'dimensoes_mm':np.round(m.extents,2).tolist(),'volume_mm3':round(m.volume,2),'fechada':bool(m.is_watertight),'componentes':1})
combined=tm.util.concatenate([m for _,m in assembly]);combined.export(OUT/'montagem_referencia.stl')
(OUT/'validacao.json').write_text(json.dumps({'unidade':'mm','entre_eixos_mm':400,'espessura_nominal_mm':2,'pecas':report},indent=2))
# Prévia geométrica fiel às malhas STL.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(16,9),facecolor='#f2f4f8')
colors=plt.cm.tab20(np.linspace(0,1,len(assembly)))
for num,exploded in [(1,False),(2,True)]:
    ax=fig.add_subplot(1,2,num,projection='3d');ax.set_facecolor('#f2f4f8')
    for idx,(name,m) in enumerate(assembly):
        v=m.vertices.copy()
        if exploded:
            center=m.centroid
            v[:,0]+=(center[0]-310)*.22;v[:,1]+=np.sign(center[1])*32
            if 'capo' in name or 'teto' in name or 'moldura' in name or 'malas' in name:v[:,2]+=45
        coll=Poly3DCollection(v[m.faces],facecolors=colors[idx],edgecolors='none',alpha=1)
        ax.add_collection3d(coll)
    ax.set_xlim(-80,700);ax.set_ylim(-180,180);ax.set_zlim(0,230)
    ax.set_box_aspect((780,360,230));ax.view_init(elev=24,azim=-140);ax.set_axis_off()
    ax.set_title('V1 • carroceria montada' if not exploded else 'Peças separadas • vista explodida',fontsize=16)
fig.suptitle('BUICK REGAL NASCAR 1987 • estudo para RC 1:8',fontsize=22,fontweight='bold')
fig.text(.5,.08,'620 × 240 mm | altura máxima 155 mm | entre-eixos 400 mm\nGeometria inicial aproximada • sem rodas, chassi ou fixações',ha='center',fontsize=13)
plt.savefig(OUT/'previa.png',dpi=150,bbox_inches='tight');plt.close()
print(json.dumps(report,indent=2));print('Peças:',len(report))
