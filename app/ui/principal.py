from pathlib import Path

import flet as ft
import pandas as pd

from app.generadores.pdf import generar_pdfs
from app.generadores.plantilla import generar_pdfs_con_plantilla
from app.importadores.comunes import crear_df_filtrado, listar_campos
from app.servicios.configuracion import (
    cargar_configuracion,
    guardar_configuracion,
)
from app.servicios.ingesta import cargar_datos

FORMATOS_DATOS = ["xlsx", "xls", "csv", "ods"]
FILAS_PREVISTA = 10


class AppDocuGen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.df = None
        self.configuracion = cargar_configuracion()

        self.txt_archivo = ft.Text(value="", selectable=True)
        self.ddl_columna = ft.Dropdown(
            label="Columna de filtro",
            width=260,
        )
        self.txt_valor = ft.TextField(
            label="Valor de filtro",
            value=self.configuracion["valor"],
            width=260,
        )
        self.ddl_hoja = ft.Dropdown(label="Hoja (opcional)", width=200)
        self.txt_plantilla = ft.Text(value="", selectable=True)
        self.txt_css = ft.Text(value="", selectable=True)
        self.txt_salida = ft.TextField(
            label="Carpeta de salida",
            value=self.configuracion["salida"],
            width=420,
        )
        self.txt_resumen = ft.Text(value="", selectable=True)
        self.txt_registros = ft.Text(value="")
        self.barra_progreso = ft.ProgressBar(value=0, visible=False)
        self.txt_progreso = ft.Text(value="")
        self.lista_errores = ft.ListView(expand=True, spacing=2)
        self.lista_archivos = ft.ListView(expand=True, spacing=2)
        self.tabla_previa = ft.DataTable(columns=[])
        self.boton_generar = ft.FilledButton(
            "Generar documentos", icon=ft.Icons.DESCRIPTION, on_click=self.generar
        )

        self.picker_datos = ft.FilePicker()
        self.picker_plantilla = ft.FilePicker()
        self.picker_css = ft.FilePicker()
        self.picker_salida = ft.FilePicker()

        if self.configuracion["archivo"]:
            self.txt_archivo.value = self.configuracion["archivo"]

    async def elegir_datos(self, e):
        archivos = await self.picker_datos.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=FORMATOS_DATOS,
        )
        if not archivos:
            return
        self.txt_archivo.value = archivos[0].path
        self.page.update()
        self.cargar_datos_actuales()

    async def elegir_plantilla(self, e):
        archivos = await self.picker_plantilla.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["html"],
        )
        if archivos:
            self.txt_plantilla.value = archivos[0].path
        self.page.update()

    async def elegir_css(self, e):
        archivos = await self.picker_css.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["css"],
        )
        if archivos:
            self.txt_css.value = archivos[0].path
        self.page.update()

    async def elegir_salida(self, e):
        ruta = await self.picker_salida.get_directory_path()
        if ruta:
            self.txt_salida.value = ruta
        self.page.update()

    def cargar_datos_actuales(self):
        ruta = self.txt_archivo.value
        if not ruta:
            return
        self.limpiar_errores()
        try:
            hoja = self.ddl_hoja.value or None
            self.df = cargar_datos(ruta, hoja=hoja)
        except (ValueError, FileNotFoundError) as error:
            self.agregar_error(str(error))
            return

        self.actualizar_hojas()
        self.actualizar_columna()
        self.actualizar_previa()
        self.txt_registros.value = f"Registros: {len(self.df)}"
        self.page.update()

    def actualizar_hojas(self):
        ruta = Path(self.txt_archivo.value)
        if ruta.suffix.lower() in (".xlsx", ".xls", ".ods"):
            try:
                libros = pd.ExcelFile(ruta)
                self.ddl_hoja.options = [
                    ft.DropdownOption(key=nombre, text=nombre)
                    for nombre in libros.sheet_names
                ]
                self.ddl_hoja.disabled = False
            except Exception:
                self.ddl_hoja.options = []
                self.ddl_hoja.disabled = True
        else:
            self.ddl_hoja.options = []
            self.ddl_hoja.disabled = True

    def actualizar_columna(self):
        self.ddl_columna.options = [
            ft.DropdownOption(key=c, text=c) for c in listar_campos(self.df)
        ]
        columna_guardada = self.configuracion["columna"]
        self.ddl_columna.value = (
            columna_guardada if columna_guardada in self.df.columns else None
        )
        self.ddl_columna.disabled = False

    def actualizar_previa(self):
        tabla = self.df.head(FILAS_PREVISTA)
        self.tabla_previa.columns = [
            ft.DataColumn(ft.Text(str(c), weight=ft.FontWeight.BOLD))
            for c in tabla.columns
        ]
        self.tabla_previa.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v))) for v in fila],
            )
            for fila in tabla.itertuples(index=False)
        ]

    def filtrar_datos(self):
        columna = self.ddl_columna.value
        valor = self.txt_valor.value
        if not columna or not valor:
            return self.df
        try:
            return crear_df_filtrado(self.df, columna, valor)
        except ValueError as error:
            self.agregar_error(str(error))
            return None

    def generar(self, e):
        self.limpiar_errores()
        if self.df is None:
            self.agregar_error("Elegí primero un archivo de datos.")
            self.page.update()
            return

        df_filtrado = self.filtrar_datos()
        if df_filtrado is None:
            self.page.update()
            return
        if df_filtrado.empty:
            self.agregar_error(
                f"No hay registros con '{self.ddl_columna.value}' = '{self.txt_valor.value}'."
            )
            self.page.update()
            return

        total = len(df_filtrado)
        self.barra_progreso.visible = True
        self.barra_progreso.value = 0
        self.txt_progreso.value = f"0/{total}"
        self.txt_resumen.value = ""
        self.boton_generar.disabled = True
        self.page.update()

        def on_progreso(i, total):
            self.barra_progreso.value = i / total
            self.txt_progreso.value = f"{i}/{total}"
            self.page.update()

        try:
            if self.txt_plantilla.value:
                archivos = generar_pdfs_con_plantilla(
                    df_filtrado,
                    self.txt_plantilla.value,
                    self.txt_salida.value,
                    css=self.txt_css.value or None,
                    on_progreso=on_progreso,
                )
            else:
                archivos = generar_pdfs(
                    df_filtrado,
                    self.txt_salida.value,
                    on_progreso=on_progreso,
                )
        except Exception as error:
            self.agregar_error(f"Error al generar: {error}")
            self.barra_progreso.visible = False
            self.boton_generar.disabled = False
            self.page.update()
            return

        self.guardar_configuracion()
        self.lista_archivos.controls = [
            ft.Text(f"- {archivo.name}") for archivo in archivos
        ]
        self.txt_resumen.value = (
            f"Se generaron {len(archivos)} documentos en '{self.txt_salida.value}'."
        )
        self.barra_progreso.value = 1
        self.boton_generar.disabled = False
        self.page.update()

    def guardar_configuracion(self):
        self.configuracion.update(
            {
                "archivo": self.txt_archivo.value,
                "columna": self.ddl_columna.value,
                "valor": self.txt_valor.value,
                "hoja": self.ddl_hoja.value,
                "salida": self.txt_salida.value,
                "plantilla": self.txt_plantilla.value or None,
                "css": self.txt_css.value or None,
            }
        )
        guardar_configuracion(self.configuracion)

    def agregar_error(self, mensaje):
        self.lista_errores.controls.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_400),
                    ft.Text(mensaje),
                ]
            )
        )
        self.lista_errores.controls[-1].visible = True

    def limpiar_errores(self):
        self.lista_errores.controls.clear()

    def construir(self):
        self.page.title = "DocuGen"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.window.width = 900
        self.page.window.height = 780

        self.page.add(
            ft.Text("DocuGen — Generador de documentos", size=24, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Elegir archivo de datos",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self.elegir_datos,
                    ),
                    self.txt_archivo,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    self.ddl_hoja,
                    self.ddl_columna,
                    self.txt_valor,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Elegir plantilla (opcional)",
                        icon=ft.Icons.ARTICLE,
                        on_click=self.elegir_plantilla,
                    ),
                    self.txt_plantilla,
                    ft.OutlinedButton(
                        "Elegir CSS (opcional)",
                        icon=ft.Icons.PALETTE,
                        on_click=self.elegir_css,
                    ),
                    self.txt_css,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    self.txt_salida,
                    ft.OutlinedButton(
                        "Elegir carpeta",
                        icon=ft.Icons.CREATE_NEW_FOLDER,
                        on_click=self.elegir_salida,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self.txt_registros,
            ft.Container(
                content=ft.ListView(
                    controls=[self.tabla_previa],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
            ),
            ft.Row(
                [
                    self.boton_generar,
                    self.barra_progreso,
                    self.txt_progreso,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self.txt_resumen,
            ft.Row(
                [
                    ft.Text("Errores", weight=ft.FontWeight.BOLD),
                    ft.Text("Documentos generados", weight=ft.FontWeight.BOLD),
                ],
                spacing=100,
            ),
            ft.Row(
                [self.lista_errores, self.lista_archivos],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )


def main():
    ft.app(target=AppDocuGen)


if __name__ == "__main__":
    main()
