"""Parametrizacao nova da prancha: mm; X para tras, Y largura, Z para cima.

Superficies CAD analiticas/interpoladas, nunca conversao de triangulos STL.
"""
from functools import lru_cache
from itertools import permutations
import numpy as np
from scipy.interpolate import PchipInterpolator, make_interp_spline
import cadquery as cq

WIDTH, HEIGHT, DEPTH = 240.0, 65.0, 40.0
WALL, CLEARANCE = 2.0, 0.30
GRILLE_W, GRILLE_H, GRILLE_Z = 135.7, 28.0, 47.0
LAMP_W, LAMP_H, LAMP_Y, LAMP_Z = 42.0, 28.0, 94.8, 47.0
DUCT_W, DUCT_H, DUCT_Y, DUCT_Z = 52.0, 15.5, 79.0, 14.0
# Os recortes recebem as mangas traseiras; as abas externas cobrem as bordas.
HOLES = [
    ('grade', 0., GRILLE_Z, 134.3, 26.6, 1.0),
    ('farol_E', -LAMP_Y, LAMP_Z, 40.6, 26.6, 1.0),
    ('farol_D', LAMP_Y, LAMP_Z, 40.6, 26.6, 1.0),
    ('duto_E', -DUCT_Y, DUCT_Z, 50.6, 14.1, 1.0),
    ('duto_D', DUCT_Y, DUCT_Z, 50.6, 14.1, 1.0),
]
PROFILE = np.array([(0.,1.0),(1.,0.35),(2.,0.),(3.,.35),(5.,1.6),
                    (8.,2.),(23.,2.3),(25.,2.),(27.,.4),(28.,.1),
                    (29.,.4),(31.,2.8),(33.,3.4),(40.,4.1),
                    (55.,6.0),(62.,7.0),(65.,8.0)])
_section = PchipInterpolator(PROFILE[:,0], PROFILE[:,1])

def front_x(y, z):
    # Abaulamento em planta: as laterais recuam 4 mm antes da dobra do canto.
    return _section(z) + 4.0*(np.asarray(y)/116.0)**2

def spline_face(grid, us, vs):
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
    from OCP.gp import gp_Pnt
    from OCP.Geom import Geom_BSplineSurface
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    su = make_interp_spline(us, grid, k=min(3,len(us)-1), axis=0)
    sv = make_interp_spline(vs, su.c, k=min(3,len(vs)-1), axis=1)
    coeff = sv.c.transpose(1,0,2)
    poles = TColgp_Array2OfPnt(1,coeff.shape[0],1,coeff.shape[1])
    for i in range(coeff.shape[0]):
        for j in range(coeff.shape[1]):
            poles.SetValue(i+1,j+1,gp_Pnt(*coeff[i,j]))
    def knots(t):
        values, mult = np.unique(t, return_counts=True)
        ks = TColStd_Array1OfReal(1,len(values))
        ms = TColStd_Array1OfInteger(1,len(values))
        for i,(v,m) in enumerate(zip(values,mult),1):
            ks.SetValue(i,float(v)); ms.SetValue(i,int(m))
        return ks,ms
    uk,um = knots(su.t); vk,vm = knots(sv.t)
    surf = Geom_BSplineSurface(poles,uk,vk,um,vm,su.k,sv.k,False,False)
    return cq.Face(BRepBuilderAPI_MakeFace(surf,1e-7).Face())

def between_grids(a, b, us, vs):
    faces = [spline_face(g,us,vs) for g in (a,b)]
    ea,eb = [f.Edges() for f in faces]
    ca = np.array([e.Center().toTuple() for e in ea])
    cb = np.array([e.Center().toTuple() for e in eb])
    perm = min(permutations(range(4)),key=lambda p:np.linalg.norm(ca-cb[list(p)],axis=1).sum())
    caps = [cq.Face.makeRuledSurface(ea[i],eb[j]) for i,j in enumerate(perm)]
    solid = cq.Solid.makeSolid(cq.Shell.makeShell([*faces,*caps]))
    if solid.Volume()<0: solid.wrapped.Reverse()
    if not solid.isValid(): raise ValueError('Superficie CAD invalida')
    return solid

@lru_cache(maxsize=20)
def front_band(offset=0., thickness=2.):
    """Camada inteira comum a todas as interfaces, evitando superficies diferentes."""
    ys = np.linspace(-120.,120.,9)
    zs = np.unique(np.r_[np.linspace(0.,65.,66),PROFILE[:,0]])
    yy,zz = np.meshgrid(ys,zs,indexing='ij')
    xx = front_x(yy,zz)+offset
    a = np.stack([xx,yy,zz],axis=-1)
    b = a.copy(); b[:,:,0]+=thickness
    return between_grids(a,b,ys,zs)

def rounded_prism(cy,cz,w,h,x0=-5.,depth=55.,r=0.8):
    plane = cq.Plane(origin=(x0,cy,cz),xDir=(0,1,0),normal=(1,0,0))
    wp = cq.Workplane(plane).rect(w,h).extrude(depth)
    if r: wp=wp.edges('|X').fillet(min(r,w/3,h/3))
    return wp.val()

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def panel(cy,cz,w,h,offset,thickness,r=.8):
    return front_band(float(offset),float(thickness)).intersect(rounded_prism(cy,cz,w,h,r=r))

def one(shape, name='peca'):
    solids = shape.Solids()
    if len(solids)!=1 or not shape.isValid():
        raise ValueError(f'{name}: esperado 1 solido valido, encontrados {len(solids)}')
    return solids[0]

def part(name, shape, color=(.45,.48,.52), group='outros', **extra):
    return dict(name=name,shape=one(shape,name),color=color,group=group,**extra)
