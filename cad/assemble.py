"""Monta e verifica os STEP exportados; nao requer o Autodesk Fusion."""
from pathlib import Path
from itertools import combinations
import json
import gc
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from common import HOLES,rounded_prism
from details import fit_depth,plate,CHROME,BLACK,GLASS,AMBER

ROOT=Path(__file__).resolve().parents[1]

def volume(shape):
    if not shape.Solids(): return 0.
    props=GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped,props,1e-6,True,False)
    return abs(props.Mass())

def color(name):
    prefix=name[:2]
    if prefix in ('01','12','13','14'): return (.57,.60,.65)
    if prefix in ('02','07'): return CHROME
    if prefix=='05': return GLASS
    if prefix=='06': return AMBER
    if prefix=='11': return (.24,.27,.32)
    return BLACK

def load_parts():
    result=[]
    for path in sorted((ROOT/'step').glob('*.step')):
        shape=cq.importers.importStep(str(path)).val()
        assert shape.isValid() and len(shape.Solids())==1,path.name
        result.append(dict(name=path.stem,shape=shape.Solids()[0],color=color(path.stem)))
    assert len(result)==21,f'Esperados 21 componentes, encontrados {len(result)}'
    return result

def finalize_depths():
    for path in sorted((ROOT/'step').glob('*.step')):
        shape=cq.importers.importStep(str(path)).val()
        # Regera apenas a placa plana opcional, que tem 3 mm de profundidade total.
        if path.stem=='11_placa_opcional':
            shape=plate()
        else:
            shape=fit_depth(path.stem,shape)
        cq.exporters.export(shape,str(path))
        print('Dimensoes finais:',path.stem,flush=True)

def overlap_bounds(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    return all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-
               max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-5 for k in 'xyz')

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--finalize-depths',action='store_true')
    args=parser.parse_args()
    if args.finalize_depths: finalize_depths()
    parts=load_parts()
    assembly=cq.Assembly(name='BUICK_REGAL_1987_FRENTE_240MM')
    records=[]
    for p in parts:
        shape=p['shape'];bb=shape.BoundingBox()
        assembly.add(shape,name=p['name'],color=cq.Color(*p['color']))
        records.append(dict(arquivo=p['name']+'.step',solidos=1,valido=True,
                            faces_cad=len(shape.Faces()),volume_mm3=round(volume(shape),5),
                            dimensoes_xyz_mm=[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)],
                            limites_min_xyz=[round(bb.xmin,3),round(bb.ymin,3),round(bb.zmin,3)],
                            limites_max_xyz=[round(bb.xmax,3),round(bb.ymax,3),round(bb.zmax,3)]))
    dest=ROOT/'BUICK_FRENTE_MONTAGEM.step'
    assembly.export(str(dest))
    reimport=cq.importers.importStep(str(dest)).val()
    assert reimport.isValid() and len(reimport.Solids())==21
    print('Montagem reaberta: 21 solidos validos',flush=True)
    report=dict(unidade='mm',componentes=records,montagem_solidos=21,
                montagem_valida=True,folga_lateral_nominal_mm=.3,
                testado_no_fusion=False,testado_fisicamente=False,
                intersecoes=[],aberturas=[])
    front=next(p['shape'] for p in parts if p['name'].startswith('01_'))
    for name,cy,cz,w,h,r in HOLES:
        # Confere a passagem pela casca frontal ate X=20. As luvas de fixacao
        # dos para-lamas ficam mais atras, a partir de X=29.
        probe=rounded_prism(cy,cz,w-.02,h-.02,x0=-5.,depth=25.,r=r+.01)
        v=volume(front.intersect(probe))
        report['aberturas'].append(dict(nome=name,intervalo_x_verificado_mm=[-5.,20.],volume_obstrucao_mm3=round(v,6)))
        assert v<.02,(name,v)
    pairs=[(a,b) for a,b in combinations(parts,2) if overlap_bounds(a['shape'],b['shape'])]
    report['pares_com_caixas_sobrepostas']=len(pairs)
    for i,(a,b) in enumerate(pairs,1):
        intersection=a['shape'].intersect(b['shape'])
        v=volume(intersection)
        if v>.02:
            report['intersecoes'].append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,6)))
        del intersection
        if i%10==0 or i==len(pairs):
            print(f'Encaixes: {i}/{len(pairs)} pares; interferencias: {len(report["intersecoes"])}',flush=True)
            gc.collect()
    report['sem_interferencias_volumetricas']=not report['intersecoes']
    (ROOT/'validacao_cad.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert not report['intersecoes'],report['intersecoes']
    print('Validacao CAD concluida; Fusion e impressao ainda nao testados.',flush=True)

if __name__=='__main__': main()
