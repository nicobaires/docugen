certificado/
│
├── main.py                  # Punto de entrada (CLI)
│
├── app/
│   ├── __init__.py
│   │
│   ├── importadores/
│   │   ├── excel.py         # Lectura y filtrado de Excel (pandas)
│   │   ├── csv.py           # futuro
│   │   └── ods.py           # futuro
│   │
│   ├── generadores/
│   │   └── pdf.py           # Generación de certificados PDF (reportlab)
│   │
│   ├── modelos/
│   │
│   ├── servicios/
│   │
│   ├── ui/                  # llegará Flet
│   │
│   └── utils/
│
├── data/
│   └── personas.xlsx        # Datos de entrada
│
├── salida/                  # PDFs generados (se crea al ejecutar)
│
├── config/
│
├── tests/
│
└── README.md
