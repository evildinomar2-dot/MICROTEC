"""Valida os arquivos exportados e interferências volumétricas na montagem."""
from pathlib import Path
import json
import numpy as np
import trimesh as tm
p=Path(__file__).parent
manifest=json.loads((p/'validacao.json').read_text())
assert {x['peca'] for x in manifest['pecas']}=={f.stem for f in (p/'stl').glob('*.stl')}
meshes={}
for r in manifest['pecas']:
 m=tm.load_mesh(p/'stl'/(r['peca']+'.stl'))
 assert m.is_watertight and m.is_volume,r['peca']
 assert len(m.split())==1,r['peca']
 assert np.allclose(m.extents,r['dimensoes_mm'],atol=.002),r['peca']
 if r['peca']!='tala_colagem_reta':meshes[r['peca']]=m
assert np.allclose(tm.load_mesh(p/'montagem_referencia.stl').extents,[620,240,147],atol=.002)
collisions=[];tested=0
items=list(meshes.items())
for i,(na,a) in enumerate(items):
 for nb,b in items[i+1:]:
  overlap=np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])
  if np.any(overlap<.001):continue
  tested+=1
  x=tm.boolean.intersection([a,b],engine='manifold')
  if len(x.faces) and x.volume>.05:collisions.append({'a':na,'b':nb,'volume_mm3':round(x.volume,4)})
result={'arquivos_stl_verificados':len(manifest['pecas']),'todos_fechados_e_conexos':True,'dimensoes_verificadas':True,'pares_com_sobreposicao_de_caixas_testados':tested,'interferencias_volumetricas':collisions,'teste_fisico':False,'teste_de_fatiamento':False}
(p/'verificacao_exportacao.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert not collisions,'Rever interferências de montagem'
