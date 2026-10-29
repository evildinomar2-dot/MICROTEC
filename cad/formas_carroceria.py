"""Superficies da carroceria refinada, em mm, sem as abas de montagem.

O ombro e o retorno superior pertencem a uma unica casca curva. A funcao
side_y descreve a borda frontal dessa casca e permite casar o para-choque.
"""
import numpy as np
import cadquery as cq
from scipy.interpolate import PchipInterpolator
from common import between_grids,box,one

X_START,X_END=40.3,210.3
WHEEL_X,WHEEL_R,WHEEL_Z=118.,34.,18.
THICKNESS=2.

# Ordem: da borda inferior externa ate a borda interna junto ao capo.
# O maximo nominal de 65 mm fica no ombro, e o retorno desce suavemente para dentro.
SECTION=np.array([
    (115.5,0.),(116.,2.),(115.5,5.),(115.,8.),(115.2,21.),
    (116.,24.),(117.,27.),(117.,28.5),(116.8,30.),(116.,32.),
    (115.6,36.),(115.3,42.),(115.,48.),(114.8,55.),
    (114.4,60.),(113.8,62.5),(112.,64.),(109.,64.7),
    (104.,64.9),(98.,64.9)
],dtype=float)
_u=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(SECTION,axis=0),axis=1))]
_y_of_u=PchipInterpolator(_u,SECTION[:,0])
_z_of_u=PchipInterpolator(_u,SECTION[:,1])
_peak=int(np.argmax(SECTION[:,1]))
_inverse_u=np.linspace(0.,_u[_peak],12001)
_inverse_z=_z_of_u(_inverse_u)

def smoothstep(t):
    q=np.clip(np.asarray(t,dtype=float),0.,1.)
    return q*q*(3.-2.*q)

def side_y(z):
    """Y exterior da borda dianteira na subida ate Z=65.

    Inverte a mesma curva parametrica usada para construir a casca. A parte
    superior interna, depois do ponto alto, nao participa dessa inversao.
    """
    zz=np.clip(np.asarray(z,dtype=float),0.,65.)
    u=np.interp(zz,_inverse_z,_inverse_u)
    return _y_of_u(u)

def return_y(x,z):
    """Retorno do para-choque: Y120 ate X24; encontra o para-lama em X40."""
    return 120.+(side_y(z)-120.)*smoothstep((np.asarray(x)-24.)/16.)

def _longitudinal(x):
    q=np.clip((np.asarray(x)-X_START)/(X_END-X_START),0.,1.)
    return np.sin(np.pi*q)**2

def _deform_y(x,y,z):
    # A broad stamped flare surrounds the wheel, with a narrow lip at its edge.
    radius=np.sqrt((np.asarray(x)-WHEEL_X)**2+(np.asarray(z)-WHEEL_Z)**2)
    flare=3.5*(1.-smoothstep((radius-35.)/15.))
    flare*=smoothstep((np.asarray(x)-X_START)/18.)
    return flare

def top_rise(x):
    return 7.*smoothstep((np.asarray(x)-X_START)/(X_END-X_START))

def _surface_grid(xs,us):
    xx,uu=np.meshgrid(xs,us,indexing='ij')
    yy=_y_of_u(uu)
    zz=_z_of_u(uu)
    y=yy+_deform_y(xx,yy,zz)
    # A curvatura longitudinal termina com derivada nula nas duas emendas.
    z=zz+top_rise(xx)*smoothstep((zz-36.)/27.)
    return np.stack([xx,y,z],axis=-1)

def _shell():
    xs=np.linspace(X_START,X_END,25)
    us=np.unique(np.r_[_u,np.linspace(0.,_u[-1],89)])
    outside=_surface_grid(xs,us)
    along_x=np.gradient(outside,xs,axis=0,edge_order=2)
    along_u=np.gradient(outside,us,axis=1,edge_order=2)
    along_x[0,:,:]=(1.,0.,0.)
    along_x[-1,:,:]=(1.,0.,0.)
    normals=np.cross(along_u,along_x)
    normals/=np.linalg.norm(normals,axis=2)[:,:,None]
    inside=outside-THICKNESS*normals
    return between_grids(outside,inside,xs,us)

def _arch_lip():
    """Ressalto acompanha a casca; altura decresce de 1 a 0,25 mm em R35.

    A pequena borda final evita a coincidencia numerica entre duas superfices
    interpoladas independentemente, que pode invalidar a uniao CAD.
    """
    angles=np.linspace(-.65,np.pi+.65,81)
    radii=np.linspace(WHEEL_R-.5,WHEEL_R+3.,10)
    aa,rr=np.meshgrid(angles,radii,indexing='ij')
    xx=WHEEL_X+rr*np.cos(aa)
    zz=WHEEL_Z+rr*np.sin(aa)
    yy=side_y(zz)
    yy=yy+_deform_y(xx,yy,zz)
    bump=.25+.75*(1.-smoothstep((rr-WHEEL_R)/3.))
    outside=np.stack([xx,yy+bump,zz],axis=-1)
    inside=np.stack([xx,yy-1.2,zz],axis=-1)
    return between_grids(outside,inside,angles,radii)

def make_fender(sign=1):
    """Um solido sem abas; X40.3..210.3, Y98..120, Z0..72, vao Ø68 com centro em Z18."""
    shell=_shell()
    lip=_arch_lip()
    shape=shell.fuse(lip)
    wheel=cq.Solid.makeCylinder(WHEEL_R,55.,cq.Vector(WHEEL_X,70.,WHEEL_Z),cq.Vector(0,1,0))
    # The opening flares out below the wheel centre instead of forming hooks.
    lower=(cq.Workplane('XZ').polyline([(WHEEL_X-38.,-1.),
        (WHEEL_X+38.,-1.),(WHEEL_X+34.,WHEEL_Z),
        (WHEEL_X-34.,WHEEL_Z)]).close().extrude(-55.).val().translate((0.,70.,0.)))
    for sign in (-1,1):
        zs=np.linspace(0.,WHEEL_Z+.2,19);us=np.linspace(-.3,3.,9)
        zz,uu=np.meshgrid(zs,us,indexing='ij')
        xx=WHEEL_X+sign*(34.+4.*(WHEEL_Z-zz)/(WHEEL_Z+1.)+uu)
        yy=side_y(zz)+_deform_y(xx,side_y(zz),zz)
        bump=.25+.75*(1.-smoothstep(uu/3.))
        a=np.stack([xx,yy+bump,zz],axis=-1)
        b=np.stack([xx,yy-1.2,zz],axis=-1)
        shape=shape.fuse(between_grids(a,b,zs,us))
    shape=shape.cut(wheel.fuse(lower))
    # Limites precisos eliminam apenas pequenos excessos de interpolacao.
    shape=shape.intersect(box(X_START,X_END,98.,120.,0.,73.))
    shape=one(shape,'para-lama curvo')
    if sign<0: shape=shape.mirror('XZ')
    return one(shape,'para-lama curvo espelhado' if sign<0 else 'para-lama curvo')
