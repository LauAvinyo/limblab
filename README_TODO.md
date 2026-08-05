# Lista de tareas (TODO) — LimbLab

Esta lista resume las tareas de refactorización, limpieza y mejoras que debes completar. Está pensada para seguir el trabajo en _tools y para planear la parte de visualizaciones más adelante.

Formato: cada ítem incluye título corto y una frase de acción.

- [ ] Cleaning .gitignore — Eliminar la línea "src/" en la raíz si no es intencional; deduplicar entradas (archive, .vscode), y añadir ignores estándar de Python (__pycache__/, *.py[cod], .venv/, dist/, build/, .pytest_cache/). Asegurar que example_data/ y docs/ no queden ignorados. (ver [.gitignore](/Users/laura/limblab/.gitignore))

- [ ] Refactorizar herramientas a _tools — Mover scripts utilitarios y carpetas de scripts a un paquete _tools; añadir __init__.py, actualizar imports internos y añadir tests para utilidades clave.

- [ ] Estandarizar layout de paquetes — Decidir si usar layout con "src/" o raíz de paquete y aplicar de forma consistente en [limblab](/Users/laura/limblab/limblab), [limblab-cli](/Users/laura/limblab/limblab-cli) y [limblab-gui](/Users/laura/limblab/limblab-gui) y en packages/.

- [ ] Corregir dependencias entre paquetes — Verificar y actualizar dependencias de ruta en pyproject.toml (por ejemplo limblab-gui -> limblab-core). Asegurar que los path deps apunten a la carpeta correcta o usar nombres publicados.

- [ ] Añadir tests y CI — Crear suites de pytest para componentes core, tests básicos para GUI (smoke tests) y flujo de GitHub Actions para ejecutar tests en push/PR; considerar informe de coverage.

- [ ] Añadir lint/format y pre-commit — Integrar black, isort y ruff (o flake8), configurar reglas y activar pre-commit hooks para mantener estilo uniforme.

- [ ] Mejorar docs y README — Actualizar README principal con quickstart, estructura del repo y guía para contribuciones; ampliar docs/ y mkdocs.yml con ejemplos y uso de la API.

- [ ] Organizar datos de ejemplo y casos de estudio — Consolidar example_data/, case_studies/, figures/ bajo examples/ o data/; gestionar archivos grandes con Git LFS o almacenamiento externo.

- [ ] Crear módulo de visualizaciones — Diseñar paquete visualizations/ o limblab-viz; definir API para plotting/3D (vedo), añadir ejemplos y documentación; integrar cuando estés listo para la parte visual.

- [ ] Refactorizar GUI — Hacer que limblab-gui use las APIs del core (no scripts internos), corregir entry points en pyproject y añadir un script de integración/smoke run.

- [ ] Mejorar webapp y despliegue — Organizar assets frontend y output de build (ej. webapp/dist), documentar despliegue y puntos de integración con APIs backend.

- [ ] Modelos DB y migraciones — Confirmar modelos SQLModel (ej.: [limblab/database.py](/Users/laura/limblab/limblab/database.py)), añadir estrategia de migraciones (alembic o versionado simple) y tests para operaciones DB.

- [ ] Preparar packaging y releases — Definir estrategia de versionado, actualizar metadatos en pyproject, añadir changelog y GitHub Action para publicar paquetes (PyPI o índice privado).

- [ ] Limpiar archivos archivados y duplicados — Eliminar duplicados (archive vs archive/), quitar .DS_Store del repo, mover archivos grandes al directorio archive/ según política y documentar la política.

- [ ] Añadir profiling y benchmarks — Crear scripts de perfilado y benchmarks para rutas de procesamiento intensivo; opcional: añadir chequeos de regresión de rendimiento en CI.


Notas finales
- Cada ítem puede descomponerse en subtareas más pequeñas (por ejemplo, tests unitarios por módulo).
- Si quieres, genero un archivo de tareas más granular (por paquete) o creo un workflow de GitHub Actions inicial.

---
Generado automáticamente para facilitar la refactorización y la futura integración de visualizaciones.
