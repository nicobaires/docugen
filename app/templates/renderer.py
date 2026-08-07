from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS


def render_template_to_html(template_dir: Path, template_name: str, context: dict) -> str:
    """Renderiza una plantilla Jinja2 a HTML y devuelve el string resultante."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)
    return template.render(**context)


def html_to_pdf(html_string: str, base_url: Path, css_path: Path | None, output_path: Path):
    """Convierte HTML a PDF usando WeasyPrint y lo guarda en output_path."""
    html = HTML(string=html_string, base_url=str(base_url))
    if css_path and css_path.exists():
        css = CSS(filename=str(css_path))
        html.write_pdf(str(output_path), stylesheets=[css])
    else:
        html.write_pdf(str(output_path))


def render_dict_to_pdf(context: dict, template_dir: Path, template_name: str, css_path: Path | None, output_path: Path):
    """Conveniencia: renderiza un diccionario a PDF.

    - context: diccionario con keys iguales a las variables de la plantilla.
    - template_dir: carpeta donde está la plantilla y los assets.
    - template_name: nombre del archivo de plantilla (ej. 'certificate.html').
    - css_path: Path al CSS relativo o absoluto (puede ser None).
    - output_path: Path donde se guardará el PDF.
    """
    html = render_template_to_html(template_dir, template_name, context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_to_pdf(html, base_url=template_dir, css_path=css_path, output_path=output_path)
