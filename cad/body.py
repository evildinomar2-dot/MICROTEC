"""Para-choque e para-lamas novos, com encaixes internos de deslizamento."""
from pathlib import Path
import cadquery as cq
import numpy as np
from common import (front_band,front_x,between_grids,HOLES,box,rounded_prism,part,one)

def bumper():
    shape=front_band(0.,2.)
    zs=np.linspace(0.,65.,66)
    # Retornos ate X=40: mesma curva da face na uniao, sobreposicao de 1 mm.
    for sign in (-1,1):
        ys=np.array([118.,119.,120.])*sign
        ys.sort()
        yy,zz=np.meshgrid(ys,zs,indexing='ij')
        xx=front_x(yy,zz)+1.0
        a=np.stack([xx,yy,zz],axis=-1)
        b=a.copy();b[:,:,0]=40.
        shape=shape.fuse(between_grids(a,b,ys,zs))
    for _,cy,cz,w,h,r in HOLES:
        shape=shape.cut(rounded_prism(cy,cz,w,h,r=r))
    # Duas luvas internas por lado: folga de 0,30 mm para as abas dos para-lamas.
    for sign in (-1,1):
        for z in (10.,49.):
            pad=box(29.,40.,112.,118.5,z-2.,z+7.)
            slot=box(30.,41.,113.7,117.9,z-.3,z+5.3)
            pad=pad.cut(slot)
            if sign<0: pad=pad.mirror('XZ')
            shape=shape.fuse(pad)
    return one(shape,'para-choque')

def fender(sign):
    xs=np.linspace(40.3,160.3,13)
    zs=np.linspace(0.,65.,27)
    xx,zz=np.meshgrid(xs,zs,indexing='ij')
    # Ombro arredondado e relevo discreto alinhado ao friso do para-choque.
    yy=120.-10.*(zz/65.)**4 - .65*np.exp(-((zz-24.)/3.)**2)
    a=np.stack([xx,yy,zz],axis=-1)
    b=a.copy(); b[:,:,1]-=2.
    side=between_grids(a,b,xs,zs)
    # Retorno superior de 40 mm, espessura 2 mm.
    top=box(40.3,160.3,80.,111.,63.,65.)
    side=side.fuse(top)
    # Aba ao redor da roda: diametro livre 62 mm.
    ring=cq.Solid.makeCylinder(33.,6.,cq.Vector(100.3,114.,0.),cq.Vector(0,1,0))
    ring=ring.intersect(box(40.3,160.3,80.,120.,0.,65.))
    side=side.fuse(ring)
    wheel=cq.Solid.makeCylinder(31.,65.,cq.Vector(100.3,65.,0.),cq.Vector(0,1,0))
    side=side.cut(wheel)
    for z in (10.,49.):
        tab=box(30.3,42.,114.,117.6,z,z+5.)
        stem=box(40.3,44.,114.,120.,z,z+5.)
        side=side.fuse(tab,stem)
    side=one(side,'para-lama')
    if sign<0: side=side.mirror('XZ')
    return side

def build_parts():
    return [part('01_parachoque_dianteiro',bumper(),(.57,.60,.65),'carroceria'),
            part('12_paralama_esquerdo',fender(-1),(.57,.60,.65),'carroceria'),
            part('13_paralama_direito',fender(1),(.57,.60,.65),'carroceria')]

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'step';out.mkdir(exist_ok=True)
    for p in build_parts():
        dest=out/(p['name']+'.step')
        cq.exporters.export(p['shape'],str(dest))
        check=cq.importers.importStep(str(dest)).val()
        assert check.isValid() and len(check.Solids())==1
        print(p['name'],len(check.Faces()),'faces CAD; exportacao validada',flush=True)
