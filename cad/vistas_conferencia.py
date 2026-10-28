"""Vistas grandes dos STEP atuais para conferencia visual, sem alterar o CAD."""
from pathlib import Path
from assemble import load_parts
from render_vtk import render, _mesh


def main():
    root = Path(__file__).resolve().parents[1]
    parts = load_parts()
    meshes = {p['name']: _mesh(p) for p in parts}
    views = [
        ('FRENTE_AMPLA.png', dict(front=True, size=(3200,1400))),
        ('FRENTE_TRES_QUARTOS.png', dict(azimuth=-145., elevation=17., size=(3200,2000))),
        ('PARALAMA_CONFERENCIA.png', dict(azimuth=-110., elevation=14., size=(2800,1600))),
    ]
    for name, options in views:
        render(parts, root / name, meshes=meshes, **options)
        print(name, flush=True)


if __name__ == '__main__':
    main()
