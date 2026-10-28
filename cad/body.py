"""Para-choque e para-lamas novos, com encaixes internos de deslizamento."""
from pathlib import Path
import cadquery as cq
import numpy as np
from common import (front_band,front_x,between_grids,HOLES,box,rounded_prism,part,one)
from formas_carroceria import return_y,make_fender

def smoothstep(t):
    t=np.clip(t,0.,1.)
    return t*t*(3.-2.*t)

def return_patch(xs,zs,inward_a,inward_b):
    """Solido entre camadas da lateral curva; usado tambem nos encaixes."""
    xx,zz=np.meshgrid(xs,zs,indexing='ij')
    yy=return_y(xx,zz)
    a=np.stack([xx,yy-inward_a,zz],axis=-1)
    b=np.stack([xx,yy-inward_b,zz],axis=-1)
    return between_grids(a,b,xs,zs)

def attachment(z):
    pad=return_patch(np.linspace(29.,40.,9),np.linspace(z-2.,z+7.,9),.8,8.)
    slot=return_patch(np.linspace(30.,41.,10),np.linspace(z-.3,z+5.3,9),2.,6.2)
    return one(pad.cut(slot),'luva interna')

def bumper():
    shape=front_band(0.,2.).intersect(box(-5.,40.,-116.,116.,0.,65.))
    zs=np.linspace(0.,65.,66)
    # Dobras curvas substituem a antiga quina de 90 graus. Raios 4 / 2 mm.
    for sign in (-1,1):
        theta=np.linspace(0.,np.pi/2.,17)
        tt,zz=np.meshgrid(theta,zs,indexing='ij')
        xc=front_x(116.,zz)+4.
        a=np.stack([xc-4.*np.cos(tt),116.+4.*np.sin(tt),zz],axis=-1)
        b=np.stack([xc-2.*np.cos(tt),116.+2.*np.sin(tt),zz],axis=-1)
        corner=between_grids(a,b,theta,zs)
        ts=np.linspace(0.,1.,33)
        uu,zz=np.meshgrid(ts,zs,indexing='ij')
        xc=front_x(116.,zz)+4.
        xx=xc+(40.-xc)*uu
        yy=return_y(xx,zz)
        a=np.stack([xx,yy,zz],axis=-1)
        b=a.copy();b[:,:,1]-=2.
        flank=between_grids(a,b,ts,zs)
        if sign<0:
            corner=corner.mirror('XZ');flank=flank.mirror('XZ')
        shape=shape.fuse(corner,flank,tol=1e-5)
        print('Dobra',sign,'solidos',len(shape.Solids()),'valido',shape.isValid(),flush=True)
    # As linhas superior/inferior encurvam-se discretamente nas extremidades.
    xs=np.linspace(-5.,41.,17);ys=np.linspace(-122.,122.,25)
    xx,yy=np.meshgrid(xs,ys,indexing='ij')
    decay=1.-smoothstep((xx-18.)/22.)
    crown=(np.abs(yy)/120.)**4*decay
    # Margem de 0,05 mm evita contatos tangentes degenerados no centro.
    a=np.stack([xx,yy,1.0*crown-.05],axis=-1)
    b=np.stack([xx,yy,65.05-2.5*crown],axis=-1)
    limiter=between_grids(a,b,xs,ys)
    shape=shape.intersect(limiter)
    print('Contorno curvo: solidos',len(shape.Solids()),'valido',shape.isValid(),flush=True)
    assert len(shape.Solids())==1 and shape.isValid(),'Falha no contorno externo'
    for _,cy,cz,w,h,r in HOLES:
        # Recorta a face; o retorno arredondado mais atras pertence a outra
        # regiao da casca e nao deve ser eliminado pelo cortador dos farois.
        shape=shape.cut(rounded_prism(cy,cz,w,h,x0=-5.,depth=31.,r=r))
        print('Vao',_,'solidos',len(shape.Solids()),'valido',shape.isValid(),flush=True)
    # Luvas acompanham a lateral: nao deixam blocos salientes na nova curva.
    for sign in (-1,1):
        for z in (10.,49.):
            pad=attachment(z)
            if sign<0: pad=pad.mirror('XZ')
            shape=shape.fuse(pad,tol=1e-5)
            print('Luva',sign,z,'valido',shape.isValid(),flush=True)
    return one(shape,'para-choque')

def fender(sign):
    side=make_fender(1)
    for z in (10.,49.):
        xs=np.unique(np.r_[np.linspace(30.3,44.,29),40.3,41.3])
        zs=np.linspace(z,z+5.,9)
        xx,zz=np.meshgrid(xs,zs,indexing='ij')
        yy=return_y(xx,zz)
        stem=2.*smoothstep((xx-40.3)/1.)
        a=np.stack([xx,yy-2.3+stem,zz],axis=-1)
        b=np.stack([xx,yy-5.9,zz],axis=-1)
        tab=between_grids(a,b,xs,zs)
        side=side.fuse(tab)
    side=one(side,'para-lama')
    if sign<0: side=side.mirror('XZ')
    return side

def build_parts():
    yield part('01_parachoque_dianteiro',bumper(),(.57,.60,.65),'carroceria')
    right=fender(1)
    yield part('12_paralama_esquerdo',right.mirror('XZ'),(.57,.60,.65),'carroceria')
    yield part('13_paralama_direito',right,(.57,.60,.65),'carroceria')

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'step';out.mkdir(exist_ok=True)
    for p in build_parts():
        dest=out/(p['name']+'.step')
        cq.exporters.export(p['shape'],str(dest))
        check=cq.importers.importStep(str(dest)).val()
        assert check.isValid() and len(check.Solids())==1
        print(p['name'],len(check.Faces()),'faces CAD; exportacao validada',flush=True)
