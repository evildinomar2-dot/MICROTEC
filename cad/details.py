"""Grade, farois desmontaveis, lentes, dutos e acabamentos em solidos CAD."""
from pathlib import Path
import cadquery as cq
import numpy as np
from common import (panel,rounded_prism,front_band,part as _part,one,box,LAMP_Y,LAMP_Z,DUCT_Y,DUCT_Z)

BLACK=(.055,.065,.08)
CHROME=(.73,.76,.80)
GLASS=(.66,.83,.90)
AMBER=(1.,.36,.025)

DEPTHS={'02':10.,'03':20.,'04':20.,'05':6.,'06':6.,'07':5.,
        '08':30.,'09':30.,'10':10.,'11':3.}

def fit_depth(name,shape):
    """Fundo plano; a profundidade cotada inclui a curvatura da face externa."""
    target=DEPTHS.get(name[:2])
    b=shape.BoundingBox()
    if target and b.xlen>target+.005:
        shape=shape.intersect(box(b.xmin-1.,b.xmin+target,
                                b.ymin-1.,b.ymax+1.,b.zmin-1.,b.zmax+1.))
    return one(shape,name)

def part(name,shape,*args,**kwargs):
    return _part(name,fit_depth(name,shape),*args,**kwargs)

def frame(cy,cz,w,h,iw,ih,offset,depth,r=.8):
    return panel(cy,cz,w,h,offset,depth,r).cut(rounded_prism(cy,cz,iw,ih,r=min(.7,ih/5)))

def grille():
    flange=frame(0.,47.,135.7,28.,129.7,22.,-1.65,1.4)
    sleeve=frame(0.,47.,133.7,26.,129.7,22.,-.5,9.)
    masks=[box(-5.,35.,y-.5,y+.5,34.,60.) for y in np.linspace(-63.,63.,37)]
    masks.append(box(-5.,35.,-65.,65.,46.55,47.45))
    # Mascara unificada antes da intersecao: barras conectadas pelo travessao.
    mask=masks[0].fuse(*masks[1:])
    bars=front_band(-1.2,2.1).intersect(mask)
    shape=flange.fuse(sleeve,bars)
    badge=panel(-49.,40.,18.,4.,-1.85,1.0,.5)
    shape=shape.fuse(badge)
    return one(shape,'grade')

def housing(sign):
    cy=sign*LAMP_Y
    flange=panel(cy,47.,42.,28.,-1.65,1.4,1.0)
    outer=panel(cy,47.,40.,26.,-.5,20.,1.)
    interior=panel(cy,47.,37.2,23.2,1.3,22.,.6)
    shape=flange.fuse(outer.cut(interior))
    for u in (-11.4,6.4):
        shape=shape.cut(rounded_prism(cy+sign*u,47.,16.8,20.8,r=.7))
    shape=shape.cut(rounded_prism(cy+sign*18.2,47.,4.2,23.,r=.5))
    return one(shape,'carcaca farois')

def lamp_frame(cy):
    flange=frame(cy,47.,17.2,21.8,15.2,15.2,-3.3,1.2,.7)
    sleeve=frame(cy,47.,16.2,20.2,15.2,15.2,-2.35,4.85,.65)
    return one(flange.fuse(sleeve),'moldura farol')

def lens(cy):
    shape=panel(cy,47.,14.6,14.6,-3.45,5.8,.65)
    # Estrias de 0,2 mm: acabamento visual, nao uma superficie optica calculada.
    ribs=[box(-6.,25.,cy+y-.18,cy+y+.18,40.2,53.8) for y in np.linspace(-6.,6.,9)]
    mask=cq.Compound.makeCompound(ribs)
    ribs_solid=front_band(-3.65,.4).intersect(mask)
    return one(shape.fuse(ribs_solid),'lente')

def indicator(cy):
    shape=panel(cy,47.,3.6,22.4,-2.2,6.,.45)
    ribs=[box(-6.,25.,cy+y-.13,cy+y+.13,36.3,57.7) for y in (-.9,0.,.9)]
    detail=front_band(-2.4,.4).intersect(cq.Compound.makeCompound(ribs))
    return one(shape.fuse(detail),'pisca')

def duct(sign):
    cy=sign*DUCT_Y
    flange=frame(cy,DUCT_Z,52.,15.5,47.2,10.7,-1.65,1.4,1.)
    sleeve=frame(cy,DUCT_Z,50.,13.5,47.2,10.7,-.5,29.,1.)
    return one(flange.fuse(sleeve),'duto inferior')

def support():
    # Anel de retencao traseiro: livre ao redor da manga da grade, para colagem.
    return one(frame(0.,47.,135.7,28.,134.3,26.6,2.35,10.,1.),'suporte grade')

def plate():
    shape=rounded_prism(0.,15.,60.,25.,x0=-3.3,depth=3.,r=1.)
    recess=rounded_prism(0.,15.,56.,21.,x0=-3.4,depth=.9,r=.75)
    return one(shape.cut(recess),'placa')

def build_parts():
    yield part('02_grade_central',grille(),CHROME,'grade')
    for sign,side,idx in [(-1,'esquerdo','03'),(1,'direito','04')]:
        cy=sign*LAMP_Y
        yield part(f'{idx}_carcaca_farois_{side}',housing(sign),BLACK,'farois')
        for i,u in enumerate((-11.4,6.4),1):
            center=cy+sign*u
            yield part(f'05_lente_farol_{side}_{i}',lens(center),GLASS,'lentes')
            yield part(f'07_moldura_farol_{side}_{i}',lamp_frame(center),CHROME,'molduras')
        yield part(f'06_lente_pisca_{side}',indicator(cy+sign*18.2),AMBER,'lentes')
    yield part('08_duto_inferior_esquerdo',duct(-1),BLACK,'dutos')
    yield part('09_duto_inferior_direito',duct(1),BLACK,'dutos')
    yield part('10_suporte_interno_grade',support(),BLACK,'grade')
    yield part('11_placa_opcional',plate(),(.24,.27,.32),'placa')

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'step';out.mkdir(exist_ok=True)
    for p in build_parts():
        dest=out/(p['name']+'.step')
        cq.exporters.export(p['shape'],str(dest))
        check=cq.importers.importStep(str(dest)).val()
        assert check.isValid() and len(check.Solids())==1
        print(p['name'],len(check.Faces()),'faces CAD; exportacao validada',flush=True)
