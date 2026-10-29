"""Para-choque e para-lamas novos, com encaixes internos de deslizamento."""
from pathlib import Path
import cadquery as cq
import numpy as np
from common import (front_band,front_x,between_grids,HOLES,box,rounded_prism,part,one,panel)
from formas_carroceria import return_y,make_fender,top_rise

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
    slot=return_patch(np.linspace(30.,41.,10),np.linspace(z-.3,z+5.3,9),1.8,6.2)
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
    # Shoulder infills above the headlights close the corners beside the hood.
    xs=np.linspace(18.,40.,25);ts=np.linspace(0.,1.,17)
    xx,tt=np.meshgrid(xs,ts,indexing='ij')
    outer=np.minimum(119.8,return_y(xx,64.0)+.7)
    yy=98.+(outer-98.)*tt
    zz=np.full_like(xx,64.0)
    a=np.stack([xx,yy,zz],axis=-1)
    b=a.copy();b[:,:,2]-=1.8
    infill=between_grids(a,b,xs,ts)
    shape=shape.fuse(infill,infill.mirror('XZ'),tol=1e-5)
    # Integral recessed mounting lands around grille and headlight assemblies.
    for name,cy,cz,w,h,r in HOLES[:3]:
        outer=rounded_prism(cy,cz,w+7.,h+7.,r=2.)
        land=front_band(1.5,4.).intersect(outer)
        shape=shape.fuse(land,tol=1e-5)
        shape=shape.cut(rounded_prism(cy,cz,w,h,x0=-5.,depth=31.,r=r))
        pocket=front_band(-1.,4.4).intersect(rounded_prism(cy,cz,w+2.,h+2.,r=1.3))
        shape=shape.cut(pocket)
    # Raised continuous belt, with a fine inset groove and separate lower lip.
    belt=panel(0.,28.,228.,4.6,-1.0,1.4,.8)
    shape=shape.fuse(belt,tol=1e-5)
    groove=panel(0.,28.,224.,.7,-1.1,.65,.2)
    shape=shape.cut(groove)
    lower=panel(0.,3.,228.,1.5,-.65,1.0,.4)
    shape=shape.fuse(lower,tol=1e-5)
    # Raised nose of the hood: a continuous crown above the grille.
    ys=np.linspace(-58.,58.,59);ts=np.linspace(0.,1.,9)
    yy,tt=np.meshgrid(ys,ts,indexing='ij')
    crown=3.*(1.-smoothstep((np.abs(yy)-43.)/12.))
    zz=64.+(1.+crown)*tt
    xx=front_x(yy,zz)
    a=np.stack([xx,yy,zz],axis=-1)
    b=a.copy();b[:,:,0]+=2.
    shape=shape.fuse(between_grids(a,b,ys,ts),tol=1e-5)
    # Pressed shoulders beside the grille, following the inclined fascia.
    for cy in (-50.5,50.5):
        shoulder=panel(cy,47.,2.2,29.,-1.1,1.6,.65)
        shape=shape.fuse(shoulder,tol=1e-5)
    # Recessed central license panel with a closed back, not a through hole.
    back=panel(0.,15.,94.,21.,1.4,2.4,1.8)
    shape=shape.fuse(back,tol=1e-5)
    pocket=panel(0.,15.,92.,19.,-1.2,2.4,1.4)
    shape=shape.cut(pocket)
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
    # Four vertical pin seats, two on each side, underneath the hood.
    for x in (60.,185.):
        seat=return_patch(np.linspace(x-6.,x+6.,5),np.linspace(58.,61.,9),.8,25.)
        hole=cq.Solid.makeCylinder(2.3,5.,cq.Vector(x,94.,57.),cq.Vector(0,0,1))
        seat=seat.cut(hole).translate((0.,0.,float(top_rise(x))))
        side=side.fuse(seat)
    side=one(side,'para-lama')
    if sign<0: side=side.mirror('XZ')
    return side

def hood(front=None):
    # Front edge follows the bowed upper edge of the fascia. 0.3 mm gap.
    us=np.linspace(0.,1.,35);ys=np.unique(np.r_[np.linspace(-97.7,97.7,45),-58.,-54.,-50.,-46.,-42.,42.,46.,50.,54.,58.])
    uu,yy=np.meshgrid(us,ys,indexing='ij')
    nose_crown=3.*(1.-smoothstep((np.abs(yy)-43.)/12.))
    start=front_x(yy,65.+nose_crown)+2.3
    xx=start+(210.-start)*uu
    # Two longitudinal pressed ridges fade into the front and rear seams.
    fade=np.sin(np.pi*uu)**.8
    ridge=1.2*np.exp(-((np.abs(yy)-50.)/3.5)**2)
    center=2.8*(1.-smoothstep((np.abs(yy)-43.)/12.))
    zz=64.85+top_rise(xx)+nose_crown*(1.-uu)+(center+ridge)*fade
    a=np.stack([xx,yy,zz],axis=-1)
    b=a.copy();b[:,:,2]-=2.
    shape=between_grids(a,b,us,ys)
    for x in (60.,185.):
        for y in (-94.,94.):
            # Slip-fit positioning pins, not elastic snap locks.
            pin=cq.Solid.makeCylinder(2.,7.,cq.Vector(x,y,57.3),cq.Vector(0,0,1))
            support=pin.fuse(cq.Solid.makeCylinder(3.,3.,cq.Vector(x,y,61.3),cq.Vector(0,0,1)))
            shape=shape.fuse(support.translate((0.,0.,float(top_rise(x)))))
    if front is None:
        front=cq.importers.importStep(str(Path(__file__).resolve().parents[1]/'step/01_parachoque_dianteiro.step')).val()
    # Trim the leading inner lip to the fascia, with 0.3 mm rearward relief.
    shape=shape.cut(front).cut(front.translate((.3,0.,0.)))
    return one(shape,'capo')

def build_parts():
    yield part('01_parachoque_dianteiro',bumper(),(.57,.60,.65),'carroceria')
    yield part('14_capo',hood(),(.57,.60,.65),'carroceria')
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
