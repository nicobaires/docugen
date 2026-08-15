from pathlib import Path

import flet as ft

COLOR_ACENTO = ft.Colors.INDIGO_300


def _boton_secundario(texto, icono, on_click):
    return ft.OutlinedButton(
        texto,
        icon=icono,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(color=ft.Colors.with_opacity(0.6, COLOR_ACENTO), width=1),
        ),
    )


def _caja_ruta(texto):
    return ft.Container(
        content=texto,
        expand=True,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border=ft.Border.all(color=ft.Colors.with_opacity(0.3, COLOR_ACENTO), width=1),
        border_radius=8,
    )


def _seccion(titulo, icono, contenido):
    return ft.Card(
        elevation=3,
        shadow_color=ft.Colors.with_opacity(0.35, ft.Colors.INDIGO_900),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icono, size=18, color=COLOR_ACENTO),
                            ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                    ft.Container(content=contenido, margin=ft.Margin.only(top=10)),
                ],
                spacing=6,
            ),
            padding=16,
            border_radius=12,
        ),
    )
