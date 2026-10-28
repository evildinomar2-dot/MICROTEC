"""Execute dentro do Autodesk Fusion: Utilitarios > Scripts e complementos.

O Fusion importa os solidos STEP e cria arquivos F3D nativos. Nao converte
malhas STL. Os esbocos e as operacoes originais nao fazem parte de um STEP.
Requer apenas o Python e a API que acompanham o proprio Fusion.

Este script foi conferido sintaticamente, mas nao executado no Fusion pelo
autor: a API adsk nao esta instalada no ambiente de preparacao do pacote.
"""

from datetime import datetime
import json
from pathlib import Path
import tempfile
import traceback

import adsk.core
import adsk.fusion


ASSEMBLY = "BUICK_FRENTE_MONTAGEM.step"


def _is_package(folder):
    return (folder / ASSEMBLY).is_file() and (folder / "step").is_dir()


def _package_folder(ui):
    # Permite manter o script em fusion/CriarBuickF3D, sem caminhos absolutos.
    for folder in list(Path(__file__).resolve().parents)[:5]:
        if _is_package(folder):
            return folder
    dialog = ui.createFolderDialog()
    dialog.title = "Escolha a pasta extraida que contem " + ASSEMBLY
    if dialog.showDialog() != adsk.core.DialogResults.DialogOK:
        return None
    folder = Path(dialog.folder)
    if not _is_package(folder):
        raise RuntimeError(
            "A pasta escolhida nao contem a montagem STEP e a subpasta step. "
            "Extraia o ZIP inteiro e escolha a pasta principal do pacote."
        )
    return folder


def _body_count(design):
    root = design.rootComponent
    count = root.bRepBodies.count
    occurrences = root.allOccurrences
    for index in range(occurrences.count):
        count += occurrences.item(index).bRepBodies.count
    return count


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    output = None
    assembly_document = None
    report = {"gerados": [], "falhas": [], "avisos": []}

    try:
        root = _package_folder(ui)
        if root is None:
            return
        parts = sorted(
            path for path in (root / "step").iterdir()
            if path.is_file() and path.suffix.lower() in (".step", ".stp")
        )
        if not parts:
            raise RuntimeError("A pasta step esta vazia. Extraia o pacote completo.")
        jobs = [root / ASSEMBLY] + parts
        if len({path.stem.casefold() for path in jobs}) != len(jobs):
            raise RuntimeError("Ha nomes de pecas repetidos no pacote STEP.")

        output_base = root / "F3D_GERADOS"
        output_base.mkdir(exist_ok=True)
        # Uma pasta exclusiva por execucao evita sobrescrever arquivos anteriores,
        # inclusive se o script for iniciado duas vezes no mesmo segundo.
        output = Path(tempfile.mkdtemp(
            prefix=datetime.now().strftime("%Y%m%d_%H%M%S_"),
            dir=str(output_base),
        ))
        importer = app.importManager

        for index, source in enumerate(jobs):
            document = None
            try:
                import_options = importer.createSTEPImportOptions(str(source))
                document = importer.importToNewDocument(import_options)
                if document is None:
                    raise RuntimeError("O Fusion nao criou o documento da importacao.")
                design = adsk.fusion.Design.cast(
                    document.products.itemByProductType("DesignProductType")
                )
                if design is None:
                    raise RuntimeError("A importacao nao resultou em um projeto Fusion.")
                count = _body_count(design)
                if count == 0:
                    raise RuntimeError("A importacao nao produziu corpos CAD.")

                # O STEP fornece os corpos; o historico passa a registrar apenas
                # as operacoes feitas daqui em diante no Fusion.
                try:
                    if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
                        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
                except Exception as error:
                    report["avisos"].append({
                        "arquivo": source.name,
                        "mensagem": "Solido importado sem ativar novo historico: " + str(error),
                    })

                destination = output / (source.stem + ".f3d")
                if destination.exists():
                    raise RuntimeError("O destino ja existe; nenhum arquivo foi sobrescrito.")
                exporter = design.exportManager
                export_options = exporter.createFusionArchiveExportOptions(str(destination))
                if not exporter.execute(export_options):
                    raise RuntimeError("O Fusion informou falha ao exportar o F3D.")
                if not destination.is_file() or destination.stat().st_size == 0:
                    raise RuntimeError("O arquivo F3D esperado nao foi criado.")

                report["gerados"].append({
                    "origem": source.name,
                    "arquivo": destination.name,
                    "corpos_importados": count,
                    "bytes": destination.stat().st_size,
                })
            except Exception:
                report["falhas"].append({
                    "arquivo": source.name,
                    "detalhes": traceback.format_exc(),
                })
            finally:
                # Nunca fecha documentos que ja estavam abertos antes do script.
                if document is not None:
                    if index == 0:
                        assembly_document = document
                    else:
                        try:
                            document.close(False)
                        except Exception as error:
                            report["avisos"].append({
                                "arquivo": source.name,
                                "mensagem": "Documento permaneceu aberto: " + str(error),
                            })
                adsk.doEvents()

        report["total_solicitado"] = len(jobs)
        report["concluido"] = not report["falhas"]
        (output / "relatorio_fusion.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if assembly_document is not None:
            assembly_document.activate()

        message = (
            "Arquivos F3D criados: {0} de {1}.\n\nPasta:\n{2}\n\n"
            "Os corpos sao editaveis. Os esbocos e o historico de modelagem "
            "anteriores a importacao STEP nao sao recuperados."
        ).format(len(report["gerados"]), len(jobs), output)
        if report["falhas"]:
            message += (
                "\n\nAlgumas pecas nao foram convertidas. Veja relatorio_fusion.json "
                "nessa pasta. Os F3D concluidos foram preservados."
            )
        ui.messageBox(message, "Buick Regal - conversao para Fusion")
    except Exception:
        details = traceback.format_exc()
        log_message = ""
        if output is not None:
            try:
                (output / "erro_fusion.txt").write_text(details, encoding="utf-8")
                log_message = "\nRegistro salvo em:\n" + str(output / "erro_fusion.txt")
            except Exception:
                pass
        ui.messageBox(
            "A conversao nao foi concluida." + log_message
            + "\n\nAlternativa: abra o STEP no Fusion e use Arquivo > Exportar "
            "para salvar como Fusion Archive (.f3d).\n\n" + details,
            "Buick Regal - conferir importacao",
        )


def stop(context):
    pass
