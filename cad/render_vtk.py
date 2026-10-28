"""Render CAD com normais VTK e z-buffer CPU (sem servidor grafico).

O VTK distribuido com CadQuery 2.7 neste ambiente tem apenas backend X11.
Este modulo usa VTK para preparar as normais e um rasterizador C pequeno para
resolver visibilidade por pixel, evitando os artefatos do painter do Matplotlib.
Requer cc para compilar o rasterizador em uma pasta temporaria, apenas uma vez.
Os triangulos existem somente para a previa; os STEP permanecem intactos.
"""
from pathlib import Path
import ctypes
import hashlib
import math
import subprocess
import tempfile

import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont

_C = r'''
#include <math.h>
#include <stdint.h>
void raster(int nt, const int32_t *tris, const float *verts,
            int w, int h, float *depth, float *image) {
  for (int ti=0;ti<nt;ti++) {
    const float *a=verts+6*tris[3*ti], *b=verts+6*tris[3*ti+1], *c=verts+6*tris[3*ti+2];
    float den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);
    if (fabsf(den)<1e-8f) continue;
    int xmin=(int)floorf(fminf(a[0],fminf(b[0],c[0]))), xmax=(int)ceilf(fmaxf(a[0],fmaxf(b[0],c[0])));
    int ymin=(int)floorf(fminf(a[1],fminf(b[1],c[1]))), ymax=(int)ceilf(fmaxf(a[1],fmaxf(b[1],c[1])));
    if(xmin<0)xmin=0; if(ymin<0)ymin=0; if(xmax>=w)xmax=w-1; if(ymax>=h)ymax=h-1;
    for(int y=ymin;y<=ymax;y++) for(int x=xmin;x<=xmax;x++) {
      float px=x+.5f, py=y+.5f;
      float wa=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den;
      float wb=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den;
      float wc=1.f-wa-wb;
      if(wa<-.000001f || wb<-.000001f || wc<-.000001f) continue;
      float z=wa*a[2]+wb*b[2]+wc*c[2]; int p=y*w+x;
      if(z>depth[p]) { depth[p]=z;
        for(int k=0;k<3;k++) image[3*p+k]=wa*a[3+k]+wb*b[3+k]+wc*c[3+k];
      }
    }
  }
}
'''

def _rasterizer():
    key=hashlib.sha256(_C.encode()).hexdigest()[:16]
    folder=Path(tempfile.gettempdir())/'buick_cpu_render'
    folder.mkdir(exist_ok=True)
    lib=folder/f'render_{key}.so'
    if not lib.exists():
        source=folder/f'render_{key}.c';source.write_text(_C)
        subprocess.run(['cc','-O3','-shared','-fPIC',str(source),'-o',str(lib),'-lm'],check=True,capture_output=True)
    fn=ctypes.CDLL(str(lib)).raster
    fn.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
    fn.restype=None
    return fn

def _mesh(part):
    points,faces=part['shape'].tessellate(.055,.12)
    vertices=np.asarray([p.toTuple() for p in points],dtype=np.float64)
    faces=np.asarray(faces,dtype=np.int64)
    poly=vtk.vtkPolyData()
    pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(vertices,deep=True));poly.SetPoints(pts)
    cells=vtk.vtkCellArray()
    packed=np.column_stack((np.full(len(faces),3,dtype=np.int64),faces)).ravel()
    cells.SetCells(len(faces),numpy_to_vtkIdTypeArray(packed,deep=True));poly.SetPolys(cells)
    clean=vtk.vtkCleanPolyData();clean.SetInputData(poly)
    clean.SetTolerance(1e-8);clean.Update()
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(clean.GetOutputPort())
    normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.SplittingOn()
    normals.SetFeatureAngle(35.);normals.ComputePointNormalsOn();normals.ComputeCellNormalsOff();normals.Update()
    result=normals.GetOutput()
    v=np.array(vtk_to_numpy(result.GetPoints().GetData()),dtype=np.float64)
    n=np.array(vtk_to_numpy(result.GetPointData().GetNormals()),dtype=np.float64)
    f=np.array(vtk_to_numpy(result.GetPolys().GetData()),dtype=np.int32).reshape(-1,4)[:,1:]
    return v,n,np.ascontiguousarray(f)

def _offset(name):
    sign=-1. if 'esquerdo' in name else 1.
    prefix=name[:2]
    if prefix=='14': return (0.,0.,75.)
    if prefix=='01': return (-12.,0.,0.)
    if prefix in ('12','13'): return (32.,sign*43.,13.)
    if prefix=='02': return (-45.,0.,34.)
    if prefix=='10': return (4.,0.,58.)
    if prefix in ('03','04'): return (-35.,sign*17.,12.)
    if prefix=='07': return (-57.,sign*18.,12.)
    if prefix in ('05','06'): return (-80.,sign*20.,12.)
    if prefix in ('08','09'): return (-53.,sign*7.,-5.)
    return (-65.,0.,-6.)

def _unit(v):
    v=np.asarray(v,dtype=float);return v/np.linalg.norm(v)

def _lighting(normals,color,view,name):
    key=_unit((-1.,-.5,1.6));fill=_unit((-.45,1.,.45));rim=_unit((.8,.3,1.))
    light=.32+.48*np.maximum(0.,normals@key)+.23*np.maximum(0.,normals@fill)+.14*np.maximum(0.,normals@rim)
    # Especular moderado ajuda a ler os ombros e quinas de pecas CAD.
    half=_unit(key+view)
    gloss=.13 if name[:2] not in ('02','05','06','07') else .26
    spec=gloss*np.maximum(0.,normals@half)**36
    rgb=np.asarray(color)[None,:]*light[:,None]+spec[:,None]
    return np.clip(rgb,0.,1.)

def render(parts,output_path,explode=False,front=False,detail=False,
           size=(1600,1000),meshes=None,azimuth=-145.,elevation=22.,frame_limits=None):
    """Renderiza solidos de parts (lista de dict name/shape/color) em PNG."""
    selected=[p for p in parts if not detail or ('esquerdo' in p['name'] and p['name'][:2] in ('03','05','06','07'))]
    if not selected:raise ValueError('Nenhuma peca selecionada')
    if meshes is None: meshes={p['name']:_mesh(p) for p in selected}
    if front: azimuth,elevation=180.,0.
    elif detail: azimuth,elevation=-157.,18.
    a,e=np.radians([azimuth,elevation])
    view=_unit([np.cos(a)*np.cos(e),np.sin(a)*np.cos(e),np.sin(e)])
    right=_unit(np.cross([0.,0.,1.],view));up=_unit(np.cross(view,right))
    prepared=[];bounds=[]
    for p in selected:
        vertices,normals,faces=meshes[p['name']]
        v=vertices+np.asarray(_offset(p['name']) if explode else (0.,0.,0.))
        projected=np.column_stack((v@right,v@up,v@view))
        bounds.append(projected[:,:2]);prepared.append((p,projected,normals,faces))
    points=np.concatenate(bounds)
    if frame_limits is None:
        lo=points.min(axis=0);hi=points.max(axis=0)
    else:
        lo,hi=map(np.asarray,frame_limits)
    center=(lo+hi)/2.
    ss=2;w,h=size[0]*ss,size[1]*ss
    scale=min(.91*w/(hi[0]-lo[0]),.86*h/(hi[1]-lo[1]))
    depth=np.full((h,w),-1e30,dtype=np.float32)
    image=np.empty((h,w,3),dtype=np.float32);image[:]=np.array([241.,243.,246.])/255.
    raster=_rasterizer()
    for p,projected,normals,faces in prepared:
        rgb=_lighting(normals,p['color'],view,p['name'])
        vertices=np.column_stack(((projected[:,0]-center[0])*scale+w/2.,
                                  -(projected[:,1]-center[1])*scale+h/2.,projected[:,2],rgb))
        vertices=np.ascontiguousarray(vertices,dtype=np.float32)
        raster(len(faces),faces.ctypes.data,vertices.ctypes.data,w,h,depth.ctypes.data,image.ctypes.data)
    img=Image.fromarray(np.uint8(np.clip(image,0.,1.)*255.)).resize(size,Image.Resampling.LANCZOS)
    output=Path(output_path);output.parent.mkdir(parents=True,exist_ok=True);img.save(output)
    return img

def _font(size,bold=False):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf'
    return ImageFont.truetype(path,size)

def sheet(parts,output_dir):
    """Cria PREVIA_BUICK.png e VISTA_FRONTAL.png somente quando solicitado."""
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    meshes={}
    for p in parts:
        meshes[p['name']]=_mesh(p)
        print('Malha de previa:',p['name'],len(meshes[p['name']][2]),flush=True)
    width,height=2400,1700
    result=Image.new('RGB',(width,height),(241,243,246));draw=ImageDraw.Draw(result)
    draw.text((width//2,48),'BUICK REGAL 1987 | FRENTE DE 240 mm',font=_font(45,True),fill='#14191f',anchor='mm')
    draw.text((width//2,108),'Superficies refinadas a partir da referencia — previa dos proprios STEP',font=_font(23),fill='#4a5360',anchor='mm')
    panels=[('Montagem — 21 componentes',{},(0,155)),
            ('Pecas separadas — vista explodida',{'explode':True},(1200,155)),
            ('Vista frontal — grade de 135,7 mm',{'front':True},(0,845)),
            ('Lentes e molduras independentes',{'detail':True},(1200,845))]
    with tempfile.TemporaryDirectory(prefix='buick_renders_') as temp:
        for i,(title,options,(x,y)) in enumerate(panels):
            draw.text((x+600,y+20),title,font=_font(26),fill='#252d37',anchor='mm')
            img=render(parts,Path(temp)/f'view_{i}.png',size=(1160,600),meshes=meshes,**options)
            result.paste(img,(x+20,y+55))
    draw.text((width//2,1588),'240 x 65 x 40 mm | Grade: 135,7 mm | Arco livre das rodas: 62 mm',font=_font(24),fill='#252d37',anchor='mm')
    draw.text((width//2,1640),'Modelo para refinamento. Montagem fisica e importacao no Fusion ainda nao testadas.',font=_font(22),fill='#505b69',anchor='mm')
    result.save(output/'PREVIA_BUICK.png')
    front_parts=[p for p in parts if p['name'][:2] not in ('12','13')]
    front_image=render(front_parts,output/'VISTA_FRONTAL.png',front=True,size=(1800,600),meshes=meshes)
    return result,front_image

def comparison(parts,old_step_dir,output_path):
    """Antes/depois com a mesma camera, escala, luz e enquadramento por linha."""
    import cadquery as cq
    from assemble import color
    old=[]
    for path in sorted(Path(old_step_dir).glob('*.step')):
        old.append(dict(name=path.stem,shape=cq.importers.importStep(str(path)).val(),color=color(path.stem)))
    if len(old)!=20 or len(parts)!=20:
        raise ValueError('A comparacao requer os 20 componentes de cada versao')
    datasets=(old,parts)
    meshes=[]
    for index,group in enumerate(datasets):
        meshes.append({p['name']:_mesh(p) for p in group})
        print('Comparacao: malhas',('anteriores' if index==0 else 'revisadas'),'prontas',flush=True)
    azimuth,elevation=-145.,22.
    a,e=np.radians([azimuth,elevation])
    view=_unit([np.cos(a)*np.cos(e),np.sin(a)*np.cos(e),np.sin(e)])
    right=_unit(np.cross([0.,0.,1.],view));up=_unit(np.cross(view,right))
    groups=[datasets,tuple([p for p in g if p['name'].startswith('12_')] for g in datasets)]
    result=Image.new('RGB',(2400,1620),(241,243,246));draw=ImageDraw.Draw(result)
    draw.text((1200,45),'BUICK REGAL 1987 — REVISÃO DAS CURVAS',font=_font(43,True),fill='#14191f',anchor='mm')
    draw.text((1200,103),'Mesma câmera, escala, iluminação e cores em cada comparação',font=_font(24),fill='#4a5360',anchor='mm')
    for x,label in ((600,'ANTES'),(1800,'AGORA')):
        draw.text((x,162),label,font=_font(34,True),fill='#252d37',anchor='mm')
    with tempfile.TemporaryDirectory(prefix='buick_comparacao_') as temp:
        for row,pair in enumerate(groups):
            projected=[]
            for i,group in enumerate(pair):
                vertices=np.concatenate([meshes[i][p['name']][0] for p in group])
                projected.append(np.column_stack((vertices@right,vertices@up)))
            allpoints=np.concatenate(projected)
            limits=(allpoints.min(axis=0),allpoints.max(axis=0))
            for i,group in enumerate(pair):
                img=render(group,Path(temp)/f'compare_{row}_{i}.png',size=(1180,580),
                           meshes=meshes[i],azimuth=azimuth,elevation=elevation,frame_limits=limits)
                result.paste(img,(i*1200+10,195 if row==0 else 895))
            if row==0:
                draw.text((1200,824),'Para-lama esquerdo: transição do topo para a lateral',font=_font(27),fill='#252d37',anchor='mm')
    draw.text((600,1506),'Topo plano e cantos mais retos',font=_font(25),fill='#4a5360',anchor='mm')
    draw.text((1800,1506),'Ombro contínuo e retornos curvos',font=_font(25),fill='#4a5360',anchor='mm')
    draw.text((1200,1570),'Geometria CAD real • Frente de 240 mm • Grade de 135,7 mm',font=_font(24),fill='#4a5360',anchor='mm')
    dest=Path(output_path);dest.parent.mkdir(parents=True,exist_ok=True);result.save(dest)
    return result

if __name__=='__main__':
    import argparse
    from assemble import load_parts
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='/workspace/scratch/render_vtk_test.png')
    parser.add_argument('--sheet-dir',default=None)
    parser.add_argument('--compare-dir',default=None)
    args=parser.parse_args()
    parts=load_parts()
    if args.compare_dir:comparison(parts,args.compare_dir,args.output)
    elif args.sheet_dir:sheet(parts,args.sheet_dir)
    else:render(parts,args.output)
    print('Render CAD concluido.',flush=True)
