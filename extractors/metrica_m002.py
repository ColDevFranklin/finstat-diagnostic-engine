# extractors/metrica_m002.py
# Métrica M002: ROE (Return on Equity)

import sys
sys.path.append('..')

import pdfplumber
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MetricaM002:
    """
    M002: ROE (Return on Equity)

    Fórmula: Utilidad Neta / Patrimonio Promedio

    Indica qué tan eficientemente el banco genera utilidades
    con el capital de los accionistas.

    Interpretación:
    - < 5%: BAJO (baja rentabilidad)
    - 5-10%: MEDIO (aceptable)
    - 10-15%: ALTO (buena rentabilidad)
    - > 15%: EXCELENTE (rentabilidad superior)
    """

    # Valores base (SIN valores por defecto - primero)
    utilidad_neta_2024: float
    utilidad_neta_2023: float
    patrimonio_2024: float
    patrimonio_2023: float
    roe_2024: float
    roe_2023: float
    nivel_desempeno: str
    pagina_fuente: int
    fecha_extraccion: str

    # Identificación (CON valores por defecto - al final)
    id: str = "M002"
    nombre: str = "ROE (Return on Equity)"

    # Análisis calculado
    cambio_yoy: float = 0.0

    def __post_init__(self):
        """Calcular cambio YoY."""
        self.cambio_yoy = self.roe_2024 - self.roe_2023

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'valores': {
                '2024': {
                    'utilidad_neta': self.utilidad_neta_2024,
                    'patrimonio': self.patrimonio_2024,
                    'roe': self.roe_2024
                },
                '2023': {
                    'utilidad_neta': self.utilidad_neta_2023,
                    'patrimonio': self.patrimonio_2023,
                    'roe': self.roe_2023
                }
            },
            'analisis': {
                'cambio_yoy_pp': self.cambio_yoy,
                'nivel_desempeno': self.nivel_desempeno
            },
            'metadata': {
                'pagina_fuente': self.pagina_fuente,
                'fecha_extraccion': self.fecha_extraccion
            }
        }

    def __str__(self):
        """Representación legible."""

        if self.cambio_yoy > 0:
            simbolo_cambio = "↑"
            texto_cambio = f"Mejora de {abs(self.cambio_yoy*100):.2f} pp"
        elif self.cambio_yoy < 0:
            simbolo_cambio = "↓"
            texto_cambio = f"Deterioro de {abs(self.cambio_yoy*100):.2f} pp"
        else:
            simbolo_cambio = "→"
            texto_cambio = "Sin cambio"

        emoji_desempeno = {
            "BAJO": "📉",
            "MEDIO": "📊",
            "ALTO": "📈",
            "EXCELENTE": "🚀"
        }.get(self.nivel_desempeno, "❓")

        return f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.id}: {self.nombre:<48} ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 VALORES 2024:                                            ║
║     Utilidad Neta: ${self.utilidad_neta_2024:>20,.0f} millones  ║
║     Patrimonio:    ${self.patrimonio_2024:>20,.0f} millones     ║
║     ROE:           {self.roe_2024:>20.2%}                     ║
║                                                              ║
║  📊 VALORES 2023:                                            ║
║     Utilidad Neta: ${self.utilidad_neta_2023:>20,.0f} millones  ║
║     Patrimonio:    ${self.patrimonio_2023:>20,.0f} millones     ║
║     ROE:           {self.roe_2023:>20.2%}                     ║
║                                                              ║
║  📈 EVOLUCIÓN YoY:                                           ║
║     {simbolo_cambio} {texto_cambio:<56} ║
║                                                              ║
║  🎯 DESEMPEÑO: {self.nivel_desempeno:<20} {emoji_desempeno:<22}║
║                                                              ║
║  📄 Fuente: Página {self.pagina_fuente:<44} ║
╚══════════════════════════════════════════════════════════════╝
        """


def extraer_metrica_m002(ruta_pdf: str) -> Optional[MetricaM002]:
    """
    Extrae y calcula ROE del PDF.
    """

    print("🚀 Extrayendo Métrica M002: ROE")
    print("-" * 70)

    if not Path(ruta_pdf).exists():
        print(f"❌ Archivo no encontrado: {ruta_pdf}")
        return None

    pdf = pdfplumber.open(ruta_pdf)

    datos = {
        'utilidad_neta_2024': None,
        'utilidad_neta_2023': None,
        'patrimonio_2024': None,
        'patrimonio_2023': None,
        'pagina_encontrada': None
    }

    # Buscar en cada página
    for numero_pagina, pagina in enumerate(pdf.pages, start=1):

        texto = pagina.extract_text()

        if not texto:
            continue

        lineas = texto.split('\n')

        for linea in lineas:
            linea_lower = linea.lower()

            # Buscar Utilidad Neta
            if ('utilidad neta' in linea_lower or 'net income' in linea_lower):

                # Excluir líneas que sean títulos o subtotales
                if 'total' not in linea_lower[:20]:  # Primeros 20 caracteres

                    numeros = extraer_numeros_de_linea(linea)

                    if len(numeros) >= 2 and not datos['utilidad_neta_2024']:
                        datos['utilidad_neta_2024'] = abs(numeros[-2])
                        datos['utilidad_neta_2023'] = abs(numeros[-1])
                        datos['pagina_encontrada'] = numero_pagina

                        print(f"📍 Página {numero_pagina} - Utilidad Neta encontrada")
                        print(f"   💰 2024: {datos['utilidad_neta_2024']:,.0f}")
                        print(f"   💰 2023: {datos['utilidad_neta_2023']:,.0f}")

            # Buscar Patrimonio
            if ('total patrimonio' in linea_lower or 'total equity' in linea_lower):

                numeros = extraer_numeros_de_linea(linea)

                if len(numeros) >= 2 and not datos['patrimonio_2024']:
                    datos['patrimonio_2024'] = abs(numeros[-2])
                    datos['patrimonio_2023'] = abs(numeros[-1])

                    print(f"📍 Página {numero_pagina} - Patrimonio encontrado")
                    print(f"   🏦 2024: {datos['patrimonio_2024']:,.0f}")
                    print(f"   🏦 2023: {datos['patrimonio_2023']:,.0f}")

            # Si tenemos ambos, validar y salir
            if datos['utilidad_neta_2024'] and datos['patrimonio_2024']:

                # Calcular ROE para validar
                roe = datos['utilidad_neta_2024'] / datos['patrimonio_2024']

                # ROE razonable: entre -10% y 30%
                if -0.10 < roe < 0.30:
                    print(f"\n✅ Datos validados (ROE preliminar: {roe:.2%})")
                    pdf.close()

                    # Calcular ROE usando patrimonio promedio
                    patrimonio_prom_2024 = (datos['patrimonio_2024'] + datos['patrimonio_2023']) / 2
                    patrimonio_prom_2023 = datos['patrimonio_2023']

                    roe_2024 = datos['utilidad_neta_2024'] / patrimonio_prom_2024
                    roe_2023 = datos['utilidad_neta_2023'] / patrimonio_prom_2023

                    nivel_desempeno = evaluar_desempeno(roe_2024)

                    metrica = MetricaM002(
                        utilidad_neta_2024=datos['utilidad_neta_2024'],
                        utilidad_neta_2023=datos['utilidad_neta_2023'],
                        patrimonio_2024=datos['patrimonio_2024'],
                        patrimonio_2023=datos['patrimonio_2023'],
                        roe_2024=roe_2024,
                        roe_2023=roe_2023,
                        nivel_desempeno=nivel_desempeno,
                        pagina_fuente=datos['pagina_encontrada'],
                        fecha_extraccion=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )

                    return metrica
                else:
                    print(f"\n⚠️  ROE fuera de rango ({roe:.2%}), continuando...")
                    datos['utilidad_neta_2024'] = None
                    datos['patrimonio_2024'] = None

    pdf.close()
    print("\n❌ No se encontraron datos suficientes")
    return None


def extraer_numeros_de_linea(linea):
    """Extrae números de una línea."""
    numeros = []
    patron = r'\(?([\d,]+)\)?'
    matches = re.findall(patron, linea)

    for match in matches:
        numero_str = match.replace(',', '')
        try:
            numero = float(numero_str)
            if numero > 1000:
                numeros.append(numero)
        except ValueError:
            continue

    return numeros


def evaluar_desempeno(roe: float) -> str:
    """Evalúa el desempeño basado en ROE."""
    if roe < 0.05:
        return "BAJO"
    elif roe < 0.10:
        return "MEDIO"
    elif roe < 0.15:
        return "ALTO"
    else:
        return "EXCELENTE"


# Código de prueba
if __name__ == "__main__":

    ruta = "../data/inputs/bancolombia_2024.pdf"

    print("="*70)
    print("🎯 PRUEBA DE MÉTRICA M002")
    print("="*70 + "\n")

    metrica = extraer_metrica_m002(ruta)

    if metrica:
        print("\n" + "="*70)
        print("✅ EXTRACCIÓN COMPLETA")
        print("="*70)
        print(metrica)
    else:
        print("\n❌ La extracción falló")
