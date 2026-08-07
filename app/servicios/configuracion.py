import json
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent.parent
RUTA_CONFIG = PROYECTO / "config" / "config.json"

DEFAULTS = {
    "archivo": str(PROYECTO / "data" / "personas.csv"),
    "columna": "Estado",
    "valor": "Aprobado",
    "hoja": None,
    "salida": str(PROYECTO / "salida"),
    "plantilla": None,
    "css": None,
}

CAMPOS_RUTA = ("archivo", "salida", "plantilla", "css")


def _resolver_rutas(configuracion):
    for campo in CAMPOS_RUTA:
        valor = configuracion.get(campo)
        if valor:
            ruta = Path(valor)
            if not ruta.is_absolute():
                ruta = PROYECTO / ruta
            configuracion[campo] = str(ruta.expanduser().resolve())


def cargar_configuracion():
    configuracion = dict(DEFAULTS)
    try:
        with open(RUTA_CONFIG, encoding="utf-8") as archivo:
            guardada = json.load(archivo)
        configuracion.update({k: v for k, v in guardada.items() if k in DEFAULTS})
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    _resolver_rutas(configuracion)
    return configuracion


def guardar_configuracion(configuracion):
    _resolver_rutas(configuracion)
    RUTA_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_CONFIG, "w", encoding="utf-8") as archivo:
        json.dump(configuracion, archivo, indent=2, ensure_ascii=False)


def restablecer_configuracion():
    try:
        RUTA_CONFIG.unlink()
    except FileNotFoundError:
        pass
