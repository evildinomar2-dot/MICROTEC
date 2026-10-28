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
    """Preserva a espessura completa das pecas na face inclinada."""
    # Preserve wall depth along the inclined face. Clipping to a global X
    # length would erase the upper rims when the face leans backwards.
    return one(shape,name)

def part(name,shape,*args,**kwargs):
    if name[:2] in ('02','03','04','05','06','07','10'):
        shape=shape.translate((3.35,0.,0.))
    if name[:2] in ('03','04'):
        fascia=cq.importers.importStep(str(Path(__file__).resolve().parents[1]/'step/01_parachoque_dianteiro.step')).val()
        sign=-1 if name[:2]=='03' else 1
        shape=shape.cut(fascia).cut(fascia.translate((0.,-sign*.3,0.)))
    return _part(name,fit_depth(name,shape),*args,**kwargs)

def frame(cy,cz,w,h,iw,ih,offset,depth,r=.8):
    return panel(cy,cz,w,h,offset,depth,r).cut(rounded_prism(cy,cz,iw,ih,r=min(.7,ih/5)))

def grille():
    flange=frame(0.,47.,95.,26.,89.,20.,-1.65,1.4)
    sleeve=frame(0.,47.,93.,24.,89.,20.,-.5,9.)
    masks=[box(-5.,35.,y-.5,y+.5,35.,59.) for y in np.linspace(-43.,43.,35)]
    masks.append(box(-5.,35.,-45.,45.,46.65,47.35))
    # Mascara unificada antes da intersecao: barras conectadas pelo travessao.
    mask=masks[0].fuse(*masks[1:])
    bars=front_band(-1.2,2.1).intersect(mask)
    shape=flange.fuse(sleeve,bars)
    badge=panel(-32.,40.,14.,3.,-1.85,1.0,.5)
    shape=shape.fuse(badge)
    return one(shape,'grade')

def housing(sign):
    cy=sign*LAMP_Y
    flange=panel(cy,47.,58.,20.,-1.65,1.4,1.0)
    outer=panel(cy,47.,56.,18.,-.5,20.,1.)
    interior=panel(cy,47.,53.2,15.2,1.3,22.,.6)
    shape=flange.fuse(outer.cut(interior))
    for u in (-14.,11.):
        shape=shape.cut(rounded_prism(cy+sign*u,47.,23.6,16.6,r=.7))
    shape=shape.cut(rounded_prism(cy+sign*26.3,47.,4.2,17.2,r=.5))
    return one(shape,'carcaca farois')

def lamp_frame(cy):
    flange=frame(cy,47.,24.,17.,21.6,13.6,-3.3,1.2,.7)
    sleeve=frame(cy,47.,23.,16.,21.6,13.6,-2.35,4.85,.65)
    return one(flange.fuse(sleeve),'moldura farol')

def lens(cy):
    shape=panel(cy,47.,21.,13.,-3.45,5.8,.65)
    # Estrias de 0,2 mm: acabamento visual, nao uma superficie optica calculada.
    ribs=[box(-6.,25.,cy+y-.18,cy+y+.18,41.,53.) for y in np.linspace(-9.,9.,13)]
    mask=cq.Compound.makeCompound(ribs)
    ribs_solid=front_band(-3.65,.4).intersect(mask)
    return one(shape.fuse(ribs_solid),'lente')

def indicator(cy):
    shape=panel(cy,47.,3.6,16.6,-2.2,6.,.45)
    ribs=[box(-6.,25.,cy+y-.13,cy+y+.13,39.2,54.8) for y in (-.9,0.,.9)]
    detail=front_band(-2.4,.4).intersect(cq.Compound.makeCompound(ribs))
    return one(shape.fuse(detail),'pisca')

def duct(sign):
    cy=sign*DUCT_Y
    flange=frame(cy,DUCT_Z,55.,12.,50.2,7.2,-1.65,1.4,1.)
    sleeve=frame(cy,DUCT_Z,53.,10.,50.2,7.2,-.5,29.,1.)
    return one(flange.fuse(sleeve),'duto inferior')

def support():
    # Anel de retencao traseiro: livre ao redor da manga da grade, para colagem.
    return one(frame(0.,47.,95.,26.,93.6,24.6,2.35,10.,1.),'suporte grade')

def plate():
    shape=rounded_prism(0.,15.,50.,16.,x0=-3.3,depth=3.,r=1.)
    recess=rounded_prism(0.,15.,46.,12.,x0=-3.4,depth=.9,r=.75)
    return one(shape.cut(recess),'placa')

def build_parts():
    yield part('02_grade_central',grille(),CHROME,'grade')
    for sign,side,idx in [(-1,'esquerdo','03'),(1,'direito','04')]:
        cy=sign*LAMP_Y
        yield part(f'{idx}_carcaca_farois_{side}',housing(sign),BLACK,'farois')
        for i,u in enumerate((-14.,11.),1):
            center=cy+sign*u
            yield part(f'05_lente_farol_{side}_{i}',lens(center),GLASS,'lentes')
            yield part(f'07_moldura_farol_{side}_{i}',lamp_frame(center),CHROME,'molduras')
        yield part(f'06_lente_pisca_{side}',indicator(cy+sign*26.3),AMBER,'lentes')
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
