"""Previa raster dos proprios solidos STEP, sem alterar os arquivos CAD."""
from pathlib import Path
import gc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from assemble import load_parts

ROOT=Path(__file__).resolve().parents[1]
LIGHT=np.array([-1.,-.5,1.8]);LIGHT/=np.linalg.norm(LIGHT)

def triangles(part):
    verts,faces=part['shape'].tessellate(.05,.12)
    vertices=np.array([v.toTuple() for v in verts])
    tri=vertices[np.asarray(faces)]
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    norms=np.linalg.norm(normals,axis=1)
    normals/=np.maximum(norms[:,None],1e-12)
    # Iluminacao de duas faces: o STEP pode orientar as faces ao contrario
    # durante a tessellacao de superficies costuradas.
    shade=.62+.38*np.abs(normals@LIGHT)
    colors=np.clip(np.array(part['color'])[None,:]*shade[:,None],0,1)
    return tri,colors

def displacement(name):
    side=-1 if 'esquerdo' in name else 1
    prefix=name[:2]
    if prefix=='14': return (0.,0.,65.)
    if prefix=='01': return (-12.,0.,0.)
    if prefix in ('12','13'): return (35.,side*48.,13.)
    if prefix=='02': return (-45.,0.,37.)
    if prefix=='10': return (4.,0.,58.)
    if prefix in ('03','04'): return (-35.,side*17.,12.)
    if prefix=='07': return (-57.,side*18.,12.)
    if prefix in ('05','06'): return (-80.,side*20.,12.)
    if prefix in ('08','09'): return (-53.,side*7.,-5.)
    return (-65.,0.,-6.)

def draw(ax,meshes,explode=False,front=False,detail=False):
    allverts=[]
    alltris=[]
    allcolors=[]
    for name,tri,colors in meshes:
        if detail and not ('esquerdo' in name and name[:2] in ('03','05','06','07')): continue
        moved=tri+np.array(displacement(name) if explode else (0,0,0))[None,None,:]
        alltris.append(moved)
        allcolors.append(colors)
        allverts.append(moved.reshape(-1,3))
    collection=Poly3DCollection(np.concatenate(alltris),facecolors=np.concatenate(allcolors),
                                linewidths=0,edgecolors='none',rasterized=True,zsort='average')
    ax.add_collection3d(collection)
    points=np.concatenate(allverts)
    low=points.min(axis=0);high=points.max(axis=0)
    extent=high-low;pad=np.maximum(extent*.045,2.)
    for dim,fn in enumerate((ax.set_xlim,ax.set_ylim,ax.set_zlim)):
        fn(low[dim]-pad[dim],high[dim]+pad[dim])
    ax.set_box_aspect(extent+2*pad,zoom=1.35 if front else 1.18)
    ax.set_proj_type('ortho')
    ax.view_init(elev=0 if front else 22,azim=180 if front else -145)
    ax.set_axis_off()
    ax.set_facecolor('#f1f3f6')

def main():
    parts=load_parts()
    meshes=[]
    for p in parts:
        tri,c=triangles(p)
        meshes.append((p['name'],tri,c))
        print(p['name'],len(tri),'triangulos apenas para previa',flush=True)
    fig=plt.figure(figsize=(19,13),facecolor='#f1f3f6')
    gs=fig.add_gridspec(2,2,left=.025,right=.975,top=.89,bottom=.09,wspace=.015,hspace=.04)
    panels=[('Montagem — 21 componentes',False,False,False),
            ('Peças separadas — vista explodida',True,False,False),
            ('Vista frontal — grade de 95 mm',False,True,False),
            ('Faróis — lentes e molduras independentes',False,False,True)]
    for slot,(title,exploded,front,detail) in zip(gs,panels):
        ax=fig.add_subplot(slot,projection='3d')
        draw(ax,meshes,exploded,front,detail)
        ax.set_title(title,fontsize=15,pad=0,fontweight='medium')
    fig.suptitle('BUICK REGAL 1987  |  FRENTE DE 240 mm',fontsize=25,fontweight='bold',y=.965)
    fig.text(.5,.923,'Prévia dos sólidos CAD exportados • nova interpretação da prancha',ha='center',fontsize=13,color='#454c57')
    fig.text(.5,.052,'Frente 240 × 65 × 40 mm  |  Para-lamas com arco livre Ø 62 mm  |  Folga nominal de encaixe: 0,30 mm',ha='center',fontsize=12)
    fig.text(.5,.027,'Lentes reduzidas para caber na frente escolhida. Modelo para refinamento; montagem física e Fusion ainda não testados.',ha='center',fontsize=11,color='#555d69')
    fig.savefig(ROOT/'PREVIA_BUICK.png',dpi=130,facecolor=fig.get_facecolor())
    plt.close(fig);gc.collect()
    # Vista frontal maior, sem o espaco ocupado pela profundidade dos para-lamas.
    onlyfront=[m for m in meshes if m[0][:2] not in ('12','13')]
    fig=plt.figure(figsize=(14,5),facecolor='#f1f3f6')
    ax=fig.add_axes([0.,0.,1.,.9],projection='3d')
    draw(ax,onlyfront,front=True)
    fig.suptitle('BUICK REGAL 1987 — frente de 240 mm',fontsize=18,y=.98)
    fig.savefig(ROOT/'VISTA_FRONTAL.png',dpi=150,facecolor=fig.get_facecolor())
    plt.close(fig)
    print('Previas salvas.',flush=True)

if __name__=='__main__': main()
