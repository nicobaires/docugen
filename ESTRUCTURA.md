# ESTRUCTURA.md

Propuesta mínima de estructura para mantener archivos pequeños y separados por responsabilidad.

Root
- README.md                # descripción corta y comandos básicos
- ROADMAP.md               # visión y próximos pasos (resumen)
- ESTRUCTURA.md            # este archivo
- pyproject.toml
- data/                    # ejemplos de datos (personas.csv)
- salida/                  # carpeta donde se generan PDFs

app/
- __init__.py
- cli.py                   # entrada CLI y orquestación
- servicios/               # funciones de alto nivel (ingesta, configuración)
- importadores/            # adaptadores que devuelven DataFrame (csv, excel, ods, dbs)
- generadores/             # lógica que genera documentos (reportlab, weasyprint)
- templates/               # renderer de plantillas (Jinja2 → HTML → PDF)

templates/
- example/
  - certificate.html
  - styles.css

scripts/
- run_template_example.py   # script demostrativo para renderizar plantillas usando data/personas.csv

Principios:
- Cada módulo hace una sola cosa y tiene tests propios.
- Evitar archivos enormes separando importadores, servicios y generadores.
- Mantener ejemplos (templates/ y data/) para que cualquier cambio tenga reproducciones fáciles.
