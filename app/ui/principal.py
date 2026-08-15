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
COLOR_ACENTO = ft.Colors.INDIGO_300


class AppDocuGen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.df = None
        self.configuracion = cargar_configuracion()

        self.txt_archivo = ft.Text(value="", selectable=True)
        self.ddl_columna = ft.Dropdown(
            label="Columna de filtro",
            width=260,
            on_select=self.al_cambiar_columna,
        )
        self.ddl_valor = ft.Dropdown(
            label="Valor de filtro",
            width=260,
            editable=True,
            enable_filter=True,
            enable_search=True,
            on_select=self.al_cambiar_valor,
            on_text_change=self.al_cambiar_valor,
        )
        self.ddl_hoja = ft.Dropdown(
            label="Hoja (opcional)",
            width=200,
            on_select=self.al_cambiar_hoja,
        )
        self.txt_plantilla = ft.Text(value="", selectable=True)
        self.txt_salida = ft.TextField(
            label="Carpeta de salida",
            value=self.configuracion["salida"],
            width=400,
        )
        self.txt_resumen = ft.Text(value="", selectable=True)
        self.txt_registros = ft.Text(value="")
        self.barra_progreso = ft.ProgressBar(
            value=0,
            visible=False,
            width=420,
            color=COLOR_ACENTO,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.INDIGO_100),
        )
        self.txt_progreso = ft.Text(value="")
        self.lista_errores = ft.ListView(spacing=4)
        self.lista_archivos = ft.ListView(spacing=2)
        self.tabla_previa = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(""))],
            visible=False,
        )
        self.boton_generar = ft.FilledButton(
            "Generar documentos",
            icon=ft.Icons.DESCRIPTION,
            on_click=self.generar,
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                elevation=4,
                shadow_color=ft.Colors.with_opacity(0.5, ft.Colors.INDIGO_900),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        self.picker_datos = ft.FilePicker()
        self.picker_plantilla = ft.FilePicker()
        self.picker_salida = ft.FilePicker()

        if self.configuracion["archivo"]:
            self.txt_archivo.value = self.configuracion["archivo"]

        self.construir()

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
        self.actualizar_valores()

    def actualizar_valores(self):
        columna = self.ddl_columna.value
        if not columna or columna not in self.df.columns:
            self.ddl_valor.options = []
            self.ddl_valor.disabled = True
            return
        valores = sorted(self.df[columna].dropna().astype(str).unique().tolist())
        self.ddl_valor.options = [
            ft.DropdownOption(key=v, text=v) for v in valores
        ]
        self.ddl_valor.disabled = False

    def filtrar_datos(self):
        columna = self.ddl_columna.value
        valor = self.ddl_valor.value
        if not columna or not valor:
            return self.df
        try:
            return crear_df_filtrado(self.df, columna, valor)
        except ValueError as error:
            self.agregar_error(str(error))
            return None

    def al_cambiar_columna(self, e):
        self.actualizar_valores()
        self.actualizar_previa()
        self.page.update()

    def al_cambiar_valor(self, e):
        self.actualizar_previa()
        self.page.update()

    def al_cambiar_hoja(self, e):
        self.cargar_datos_actuales()

    def actualizar_previa(self):
        if self.df is None:
            return
        filtrado = self.filtrar_datos()
        if filtrado is None:
            return
        tabla = filtrado.head(FILAS_PREVISTA)
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
        self.tabla_previa.visible = True

        columna = self.ddl_columna.value
        valor = self.ddl_valor.value
        if columna and valor:
            self.txt_registros.value = (
                f"Registros: {len(self.df)}   filtrados: {len(filtrado)}"
            )
        else:
            self.txt_registros.value = f"Registros: {len(self.df)}"

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
                f"No hay registros con '{self.ddl_columna.value}' = '{self.ddl_valor.value}'."
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
                "valor": self.ddl_valor.value,
                "hoja": self.ddl_hoja.value,
                "salida": self.txt_salida.value,
                "plantilla": self.txt_plantilla.value or None,
                "css": None,
            }
        )
        guardar_configuracion(self.configuracion)

    def agregar_error(self, mensaje):
        self.lista_errores.controls.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_400),
                    ft.Text(mensaje),
                ],
                spacing=6,
            )
        )

    def limpiar_errores(self):
        self.lista_errores.controls.clear()

    def _boton_secundario(self, texto, icono, on_click):
        return ft.OutlinedButton(
            texto,
            icon=icono,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(
                    color=ft.Colors.with_opacity(0.6, COLOR_ACENTO), width=1
                ),
            ),
        )

    def _caja_ruta(self, texto):
        return ft.Container(
            content=texto,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border=ft.Border.all(
                color=ft.Colors.with_opacity(0.3, COLOR_ACENTO), width=1
            ),
            border_radius=8,
        )

    def _seccion(self, titulo, icono, contenido):
        return ft.Card(
            elevation=3,
            shadow_color=ft.Colors.with_opacity(0.35, ft.Colors.INDIGO_900),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icono, size=18, color=COLOR_ACENTO),
                                ft.Text(
                                    titulo,
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Container(
                            content=contenido, margin=ft.Margin.only(top=10)
                        ),
                    ],
                    spacing=6,
                ),
                padding=16,
                border_radius=12,
            ),
        )

    def construir(self):
        self.page.title = "DocuGen"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
        self.page.padding = 16
        self.page.window.width = 1060
        self.page.window.height = 900
        self.page.scroll = ft.ScrollMode.AUTO

        self.page.appbar = ft.AppBar(
            title=ft.Text("DocuGen", size=22, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.INDIGO_900,
        )

        if not self.txt_archivo.value:
            self.txt_registros.value = "Elegí un archivo de datos para comenzar."

        self.page.add(
            self._seccion(
                "Datos de origen",
                ft.Icons.FOLDER_OPEN,
                ft.Column(
                    [
                        ft.Row(
                            [
                                self._boton_secundario(
                                    "Elegir archivo",
                                    ft.Icons.FOLDER_OPEN,
                                    self.elegir_datos,
                                ),
                                self._caja_ruta(self.txt_archivo),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [self.ddl_hoja, self.ddl_columna, self.ddl_valor],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        self.txt_registros,
                    ],
                    spacing=10,
                ),
            ),
            self._seccion(
                "Plantilla",
                ft.Icons.ARTICLE,
                ft.Row(
                    [
                        self._boton_secundario(
                            "Elegir plantilla",
                            ft.Icons.ARTICLE,
                            self.elegir_plantilla,
                        ),
                        self._caja_ruta(self.txt_plantilla),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            self._seccion(
                "Carpeta de salida",
                ft.Icons.CREATE_NEW_FOLDER,
                ft.Row(
                    [
                        self.txt_salida,
                        self._boton_secundario(
                            "Elegir carpeta",
                            ft.Icons.CREATE_NEW_FOLDER,
                            self.elegir_salida,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            self._seccion(
                "Vista previa",
                ft.Icons.TABLE_VIEW,
                ft.Container(
                    content=ft.ListView(
                        controls=[self.tabla_previa],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    height=260,
                ),
            ),
            self._seccion(
                "Generación",
                ft.Icons.AUTO_AWESOME,
                ft.Column(
                    [
                        ft.Row(
                            [
                                self.boton_generar,
                                self.barra_progreso,
                                self.txt_progreso,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        self.txt_resumen,
                    ],
                    spacing=8,
                ),
            ),
            self._seccion(
                "Resultados",
                ft.Icons.LIST_ALT,
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Errores",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.RED_300,
                                ),
                                ft.Container(expand=True),
                                ft.Text(
                                    "Documentos generados",
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    content=self.lista_errores, expand=True
                                ),
                                ft.VerticalDivider(),
                                ft.Container(
                                    content=self.lista_archivos, expand=True
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ],
                    spacing=8,
                ),
            ),
        )


def main():
    ft.app(target=AppDocuGen)


if __name__ == "__main__":
    main()
