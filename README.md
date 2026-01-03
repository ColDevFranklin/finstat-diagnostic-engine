# FinStat Diagnostic Engine

Sistema automático para extraer métricas financieras de estados financieros bancarios.

## Instalación

```bash

# 1. Clonar repositorio
git clone [tu-url-aqui]
cd finstat-diagnostic-engine

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

## Uso Básico

```bash
python scripts/run_diagnostic.py --pdf ruta/al/archivo.pdf
```

## Estructura del Proyecto

```
finstat-diagnostic-engine/
├── config/          # Configuraciones
├── parsers/         # Extracción de PDF
├── extractors/      # Cálculo de métricas
├── analyzers/       # Comparación vs benchmarks
├── generators/      # Generación de reportes
├── data/            # PDFs y benchmarks
└── scripts/         # Scripts ejecutables
```

## Autor

Franklin Rodriguez - Sistema Franklin™
