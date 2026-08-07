# 🗺️ Roadmap (resumido)

Este archivo es una versión enfocada del ROADMAP original para uso práctico: Now (hacer ya), Next (seguir después) y Later (ideas lejanas). Cada ítem incluye un criterio de aceptación y una estimación.

## Now (prioridad alta — siguiente sprint)

- Implementar motor de plantillas (v0.2)
  - Criterio de aceptación: existe `templates/example/certificate.html` y `app/templates/renderer.py` que renderiza una fila (o diccionario) a PDF usando Jinja2 + WeasyPrint; incluye un script de ejemplo `scripts/run_template_example.py` que genera al menos 1 PDF.
  - Estimación: M (1–2 días)

- Añadir ESTRUCTURA.md
  - Criterio de aceptación: archivo en la raíz que documenta convenciones de carpetas y contratos entre módulos.
  - Estimación: S (1–2 horas)

## Next (prioridad media)

- Configuración persistente (v0.3)
  - Criterio de aceptación: formato de config (`.docugen.toml` o similar) y carga/guardado automático de último archivo, plantilla y carpeta de salida.
  - Estimación: M (2–3 días)

- Tests básicos y CI
  - Criterio de aceptación: pipeline en GitHub Actions que instala dependencias y corre una pequeña suite de tests (importadores + render básico).
  - Estimación: M (2–4 días)

## Later (ideas a largo plazo)

- Editor visual de plantillas (v2.x)
- Plantillas reutilizables como paquetes
- Importadores adicionales (Google Sheets, DBs)
- Automatización (envío por correo, ZIP, firma digital)

---

Notas:
- Mantené el ROADMAP en la raíz como visión, pero vinculalo a issues/milestones si querés seguimiento formal.
