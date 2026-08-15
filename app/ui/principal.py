from pathlib import Path
import logging
import os
import webbrowser

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
from app.ui.sections import _seccion, _caja_ruta, _boton_secundario

FORMATOS_DATOS = ["xlsx", "xls", "csv", "ods"]
FILAS_PREVISTA = 10


# logging
LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_DIR / "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


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
            value=self.configuracion.get("salida", ""),
            width=400,
        )
        self.txt_resumen = ft.Text(value="", selectable=True)
        self.txt_registros = ft.Text(value="")
        self.barra_progreso = ft.ProgressBar(
            value=0,
            visible=False,
            width=420,
            color=ft.Colors.INDIGO_300,
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

        if self.configuracion.get("archivo"):
            self.txt_archivo.value = self.configuracion.get("archivo")

        self._build_progress_dialog()
        self.construir()

    def _build_progress_dialog(self):
        # AlertDialog used as modal progress indicator
        self.progress_dialog_progress = ft.ProgressBar(value=0, width=360)
        self.progress_dialog_text = ft.Text(value="")
        self.progress_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Procesando..."),
            content=ft.Column([
                self.progress_dialog_progress,
                ft.Container(height=8),
                self.progress_dialog_text,
            ]),
            actions=[],
        )

    def _show_progress(self):
        self.page.dialog = self.progress_dialog
        self.progress_dialog.open = True
        self.page.update()

    def _hide_progress(self):
        try:
            self.progress_dialog.open = False
            self.page.update()
        except Exception:
            pass

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
            # load in background to avoid blocking UI
            def _load():
                return cargar_datos(ruta, hoja=hoja)

            self.df = self.page.run_in_threadpool(_load)
        except (ValueError, FileNotFoundError) as error:
            self.agregar_error(str(error))
            logger.exception("Error cargando datos")
            return
        except Exception as err:
            self.agregar_error(str(err))
            logger.exception("Error inesperado cargando datos")
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
            except Exception as e:
                logger.exception("Error leyendo hojas: %s", e)
                self.ddl_hoja.options = []
                self.ddl_hoja.disabled = True
        else:
            self.ddl_hoja.options = []
            self.ddl_hoja.disabled = True

    def actualizar_columna(self):
        if self.df is None:
            return
        self.ddl_columna.options = [
            ft.DropdownOption(key=c, text=c) for c in listar_campos(self.df)
        ]
        columna_guardada = self.configuracion.get("columna")
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
        self.ddl_valor.options = [ft.DropdownOption(key=v, text=v) for v in valores]
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
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in fila])
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

    async def generar(self, e):
        # Clear previous errors
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

        salida = self.txt_salida.value or ""
        salida_path = Path(salida)
        if not salida_path.exists():
            try:
                salida_path.mkdir(parents=True, exist_ok=True)
            except Exception as err:
                self.agregar_error(f"No se puede crear la carpeta de salida: {err}")
                logger.exception("Error creando carpeta de salida")
                self.page.update()
                return
        if not os.access(salida_path, os.W_OK):
            self.agregar_error("No se tienen permisos de escritura en la carpeta de salida.")
            self.page.update()
            return

        total = len(df_filtrado)
        self.barra_progreso.visible = True
        self.barra_progreso.value = 0
        self.txt_progreso.value = f"0/{total}"
        self.txt_resumen.value = ""
        self.boton_generar.disabled = True
        self.page.update()

        # thread-safe progress callback
        def on_progreso(i, total_local):
            try:
                def _update():
                    self.barra_progreso.value = i / total_local if total_local else 0
                    percent = int((i / total_local) * 100) if total_local else 0
                    self.txt_progreso.value = f"{percent}% — {i}/{total_local}"
                    self.progress_dialog_progress.value = self.barra_progreso.value
                    self.progress_dialog_text.value = self.txt_progreso.value
                    self.page.update()

                self.page.call_from_thread(_update)
            except Exception:
                logger.exception("Error actualizando progreso")

        # show modal
        self._show_progress()

        try:
            def _generate():
                if self.txt_plantilla.value:
                    return generar_pdfs_con_plantilla(
                        df_filtrado,
                        self.txt_plantilla.value,
                        str(salida_path),
                        on_progreso=on_progreso,
                    )
                else:
                    return generar_pdfs(
                        df_filtrado, str(salida_path), on_progreso=on_progreso
                    )

            archivos = await self.page.run_in_threadpool(_generate)
        except Exception as error:
            logger.exception("Error al generar documentos")
            self.agregar_error(f"Error al generar: {error}")
            self.barra_progreso.visible = False
            self.boton_generar.disabled = False
            self._hide_progress()
            self.page.update()
            return

        # post-process UI updates
        self.guardar_configuracion()
        self.lista_archivos.controls = [
            ft.Row([ft.Text(f"- {archivo.name}"), ft.Container(expand=True), ft.IconButton(ft.icons.OPEN_IN_NEW, on_click=lambda e, p=str(archivo): webbrowser.open(f"file://{p}"))])
            for archivo in archivos
        ]
        self.txt_resumen.value = (
            f"Se generaron {len(archivos)} documentos en '{str(salida_path)}'."
        )
        self.barra_progreso.value = 1
        self.boton_generar.disabled = False
        self._hide_progress()
        self.page.update()

        # show info dialog
        try:
            dlg = ft.AlertDialog(title=ft.Text("Generación completada"), content=ft.Text(self.txt_resumen.value), actions=[ft.TextButton("Abrir carpeta", on_click=lambda e, p=str(salida_path): webbrowser.open(f"file://{p}")), ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(e))])
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
        except Exception:
            pass

    def _close_dialog(self, e):
        try:
            self.page.dialog.open = False
            self.page.update()
        except Exception:
            pass

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
        logger.warning(mensaje)
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

    def construir(self):
        self.page.title = "DocuGen"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
        self.page.padding = 16
        try:
            self.page.window.width = 1060
            self.page.window.height = 900
        except Exception:
            pass
        self.page.scroll = ft.ScrollMode.AUTO

        self.page.appbar = ft.AppBar(
            title=ft.Text("DocuGen", size=22, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.INDIGO_900,
        )

        if not self.txt_archivo.value:
            self.txt_registros.value = "Elegí un archivo de datos para comenzar."

        self.page.add(
            _seccion(
                "Datos de origen",
                ft.Icons.FOLDER_OPEN,
                ft.Column(
                    [
                        ft.Row(
                            [
                                _boton_secundario(
                                    "Elegir archivo", ft.Icons.FOLDER_OPEN, self.elegir_datos
                                ),
                                _caja_ruta(self.txt_archivo),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row([self.ddl_hoja, self.ddl_columna, self.ddl_valor], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        self.txt_registros,
                    ],
                    spacing=10,
                ),
            ),
            _seccion(
                "Plantilla",
                ft.Icons.ARTICLE,
                ft.Row(
                    [
                        _boton_secundario("Elegir plantilla", ft.Icons.ARTICLE, self.elegir_plantilla),
                        _caja_ruta(self.txt_plantilla),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            _seccion(
                "Carpeta de salida",
                ft.Icons.CREATE_NEW_FOLDER,
                ft.Row(
                    [
                        self.txt_salida,
                        _boton_secundario("Elegir carpeta", ft.Icons.CREATE_NEW_FOLDER, self.elegir_salida),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            _seccion(
                "Vista previa",
                ft.Icons.TABLE_VIEW,
                ft.Container(
                    content=ft.ListView(controls=[self.tabla_previa], scroll=ft.ScrollMode.AUTO), height=260,
                ),
            ),
            _seccion(
                "Generación",
                ft.Icons.AUTO_AWESOME,
                ft.Column(
                    [
                        ft.Row([self.boton_generar, self.barra_progreso, self.txt_progreso], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        self.txt_resumen,
                    ],
                    spacing=8,
                ),
            ),
            _seccion(
                "Resultados",
                ft.Icons.LIST_ALT,
                ft.Column(
                    [
                        ft.Row([
                            ft.Text("Errores", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300),
                            ft.Container(expand=True),
                            ft.Text("Documentos generados", weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Row([
                            ft.Container(content=self.lista_errores, expand=True),
                            ft.VerticalDivider(),
                            ft.Container(content=self.lista_archivos, expand=True),
                        ], vertical_alignment=ft.CrossAxisAlignment.START),
                    ],
                    spacing=8,
                ),
            ),
        )


def main():
    ft.app(target=AppDocuGen)


if __name__ == "__main__":
    main()
