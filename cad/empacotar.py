"""Atualiza medidas, checksums e ZIP depois da validacao CAD."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / 'validacao_cad.json').read_text())
    assert report['montagem_solidos'] == 21
    assert report['sem_interferencias_volumetricas']
    for source in (root / 'cad').glob('*.py'):
        ast.parse(source.read_text())
    with (root / 'MEDIDAS.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream, delimiter=';', lineterminator='\n')
        writer.writerow(['arquivo', 'X_mm', 'Y_mm', 'Z_mm'])
        for component in report['componentes']:
            writer.writerow([component['arquivo'], *component['dimensoes_xyz_mm']])
    files = sorted(p for p in root.rglob('*') if p.is_file()
                   and '.git' not in p.parts and '__pycache__' not in p.parts
                   and p.suffix not in ('.zip', '.pyc') and p.name != 'SHA256SUMS.txt')
    sums = root / 'SHA256SUMS.txt'
    sums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  '
                           + p.relative_to(root).as_posix() + '\n' for p in files))
    files.append(sums)
    archive = root / 'Buick_Regal_240_CAD_Fusion.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, 'Buick_Regal_240_CAD_Fusion/' + path.relative_to(root).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert sum(n.endswith('.step') for n in bundle.namelist()) == 22
    print('ZIP validado: 21 pecas e uma montagem.')


if __name__ == '__main__':
    main()
