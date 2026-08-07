# docugen

Automatiza la generación de documentos PDF a partir de datos en Excel, CSV u ODS.

## Uso (ejemplo con plantillas)

Para probar el ejemplo de plantilla incluido:

```bash
python scripts/run_template_example.py --archivo data/personas.csv --salida salida/templates_example
```

Esto renderiza `templates/example/certificate.html` usando `data/personas.csv` y guarda PDFs en `salida/templates_example/`.

(El README original sigue vigente para el uso básico desde `main.py`.)
