from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def crear_carpeta_salida(ruta_carpeta="salida"):
    carpeta = Path(ruta_carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def _crear_estilos():
    styles = getSampleStyleSheet()

    style_titulo = ParagraphStyle(
        "TituloDocumento",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#2C3E50"),
        alignment=1,
    )

    style_cuerpo = ParagraphStyle(
        "CuerpoDocumento",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#555555"),
        alignment=1,
    )

    return style_titulo, style_cuerpo


def generar_pdfs(df, carpeta_salida="salida", on_progreso=None):
    carpeta = crear_carpeta_salida(carpeta_salida)
    style_titulo, style_cuerpo = _crear_estilos()
    archivos_generados = []
    total = len(df)

    for i, row in enumerate(df.itertuples()):
        if on_progreso:
            on_progreso(i + 1, total)
        nombre = row.Nombre
        curso = row.Curso
        estado = row.Estado

        nombre_limpio = str(nombre).strip().replace(" ", "_")
        ruta_pdf = carpeta / f"Certificado_{nombre_limpio}.pdf"

        doc = SimpleDocTemplate(
            str(ruta_pdf),
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        story = [
            Spacer(1, 150),
            Paragraph(f"¡Felicidades, {nombre}!", style_titulo),
            Spacer(1, 15),
            Paragraph(
                f"Has aprobado con éxito el curso <b>{curso}</b>.", style_cuerpo
            ),
            Spacer(1, 10),
            Paragraph(f"Estado: {estado}", style_cuerpo),
        ]

        doc.build(story)
        archivos_generados.append(ruta_pdf)

    return archivos_generados
