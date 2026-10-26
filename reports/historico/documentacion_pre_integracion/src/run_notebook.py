"""Ejecuta un notebook del proyecto y conserva sus resultados."""
from pathlib import Path
import argparse
import os
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", choices=["root", "notebooks"], default="root")
    parser.add_argument("--notebook", choices=["eda.ipynb", "preparacion.ipynb", "baseline.ipynb", "protocolo_temporal.ipynb", "comparacion_modelos.ipynb", "optimizacion.ipynb", "explicabilidad.ipynb", "correccion_sesgo_temporal.ipynb", "seleccion_final.ipynb", "evaluacion_final.ipynb"], default="eda.ipynb")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    import json
    active=root/'reports/estado_protocolo.json'
    historical_v2=['protocolo_temporal.ipynb','comparacion_modelos.ipynb','optimizacion.ipynb','explicabilidad.ipynb']
    if active.exists() and json.loads(active.read_text(encoding='utf-8')).get('vigente')=='v3_cohortes_llegada_retrospectivo' and args.notebook in historical_v2:
        raise SystemExit('Notebook histórico v2: usar copia aislada de reports/historico/protocolo_v2. No sobrescribir resultados activos v3. Notebook vigente: correccion_sesgo_temporal.ipynb.')
    notebook_path = root / "notebooks" / args.notebook
    # Configuración y cachés locales: no se registra un kernel global.
    runtime = root / ".jupyter_runtime"
    runtime.mkdir(exist_ok=True)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime)
    os.environ["MPLCONFIGDIR"] = str(runtime / "matplotlib")
    kernel_dir = runtime / "kernels" / "hotel-eda"
    kernel_dir.mkdir(parents=True, exist_ok=True)
    import json
    (kernel_dir / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Python (EDA hoteles)", "language": "python",
    }), encoding="utf-8")
    notebook = nbformat.read(notebook_path, as_version=4)
    workdir = root if args.cwd == "root" else root / "notebooks"
    manager = KernelSpecManager(kernel_dirs=[str(runtime / "kernels")])
    from jupyter_client import KernelManager
    kernel_manager = KernelManager(kernel_name="hotel-eda", kernel_spec_manager=manager)
    client = NotebookClient(notebook, timeout=240, km=kernel_manager,
                            resources={"metadata": {"path": str(workdir)}},
                            allow_errors=False)
    try:
        client.execute()
    finally:
        if kernel_manager.has_kernel:
            kernel_manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    nbformat.write(notebook, notebook_path)
    print(f"Notebook ejecutado sin errores desde {args.cwd}: {notebook_path}")


if __name__ == "__main__":
    main()
