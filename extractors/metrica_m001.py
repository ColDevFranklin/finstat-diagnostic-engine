# extractors/metrica_m001.py
# Métrica M001: Provisión/Cartera Total

import sys
sys.path.append('..')

from parsers.extraer_tabla_inteligente import extraer_tabla_provision
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MetricaM001:
    """
    M001: Provisión/Cartera Total

    Indica qué porcentaje de la cartera está provisionado.

    Interpretación:
    - < 4%: BAJO (cartera de alta calidad)
    - 4-7%: MEDIO (estándar sectorial)
    - 7-10%: ALTO (requiere monitoreo)
    - > 10%: CRÍTICO (riesgo significativo)
    """

    # Valores base (SIN valores por defecto)
    provision_2024: float
    provision_2023: float
    cartera_2024: float
    cartera_2023: float
    ratio_2024: float
    ratio_2023: float
    nivel_riesgo: str
    pagina_fuente: int
    fecha_extraccion: str

    # Identificación (CON valores por defecto - al final)
    id: str = "M001"
    nombre: str = "Provisión/Cartera Total"

    # Análisis calculado
    cambio_yoy: float = 0.0

    def __post_init__(self):
        """Se ejecuta después de crear el objeto."""
        # Calcular cambio YoY en puntos porcentuales
        self.cambio_yoy = self.ratio_2024 - self.ratio_2023

    def to_dict(self):
        """Convierte la métrica a diccionario para guardar en JSON."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'valores': {
                '2024': {
                    'provision': self.provision_2024,
                    'cartera': self.cartera_2024,
                    'ratio': self.ratio_2024
                },
                '2023': {
                    'provision': self.provision_2023,
                    'cartera': self.cartera_2023,
                    'ratio': self.ratio_2023
                }
            },
            'analisis': {
                'cambio_yoy_pp': self.cambio_yoy,
                'nivel_riesgo': self.nivel_riesgo
            },
            'metadata': {
                'pagina_fuente': self.pagina_fuente,
                'fecha_extraccion': self.fecha_extraccion
            }
        }

    def __str__(self):
        """Representación legible para la terminal."""

        # Símbolos para cambio YoY
        if self.cambio_yoy > 0:
            simbolo_cambio = "↑"
            texto_cambio = f"Incremento de {abs(self.cambio_yoy*100):.2f} pp"
        elif self.cambio_yoy < 0:
            simbolo_cambio = "↓"
            texto_cambio = f"Reducción de {abs(self.cambio_yoy*100):.2f} pp"
        else:
            simbolo_cambio = "→"
            texto_cambio = "Sin cambio"

        # Emoji según nivel de riesgo
        emoji_riesgo = {
            "BAJO": "✅",
            "MEDIO": "⚠️",
            "ALTO": "⚠️⚠️",
            "CRÍTICO": "🚨"
        }.get(self.nivel_riesgo, "❓")

        return f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.id}: {self.nombre:<48} ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 VALORES 2024:                                            ║
║     Provisión:  ${self.provision_2024:>20,.0f} millones     ║
║     Cartera:    ${self.cartera_2024:>20,.0f} millones       ║
║     Ratio:      {self.ratio_2024:>20.2%}                     ║
║                                                              ║
║  📊 VALORES 2023:                                            ║
║     Provisión:  ${self.provision_2023:>20,.0f} millones     ║
║     Cartera:    ${self.cartera_2023:>20,.0f} millones       ║
║     Ratio:      {self.ratio_2023:>20.2%}                     ║
║                                                              ║
║  📈 EVOLUCIÓN YoY:                                           ║
║     {simbolo_cambio} {texto_cambio:<56} ║
║                                                              ║
║  🎯 NIVEL DE RIESGO: {self.nivel_riesgo:<20} {emoji_riesgo:<18}║
║                                                              ║
║  📄 Fuente: Página {self.pagina_fuente:<44} ║
║  📅 Fecha: {self.fecha_extraccion:<45} ║
╚══════════════════════════════════════════════════════════════╝
        """


def extraer_metrica_m001(ruta_pdf: str) -> Optional[MetricaM001]:
    """
    Extrae y calcula la métrica M001 de un PDF.

    Parámetros:
    - ruta_pdf: ruta al archivo PDF

    Retorna:
    - Objeto MetricaM001 o None si falla
    """

    print("🚀 Extrayendo Métrica M001: Provisión/Cartera Total")
    print("-" * 70)

    # Paso 1: Extraer datos del PDF
    datos = extraer_tabla_provision(ruta_pdf)

    if not datos or not datos['provision_2024'] or not datos['cartera_2024']:
        print("❌ No se pudieron extraer los datos necesarios")
        return None

    # Paso 2: Calcular ratios
    ratio_2024 = datos['provision_2024'] / datos['cartera_2024']
    ratio_2023 = datos['provision_2023'] / datos['cartera_2023']

    print(f"\n✅ Ratios calculados:")
    print(f"   2024: {ratio_2024:.4%}")
    print(f"   2023: {ratio_2023:.4%}")

    # Paso 3: Evaluar nivel de riesgo
    nivel_riesgo = evaluar_nivel_riesgo(ratio_2024)

    print(f"\n🎯 Nivel de riesgo: {nivel_riesgo}")

    # Paso 4: Crear objeto métrica
    metrica = MetricaM001(
        provision_2024=datos['provision_2024'],
        provision_2023=datos['provision_2023'],
        cartera_2024=datos['cartera_2024'],
        cartera_2023=datos['cartera_2023'],
        ratio_2024=ratio_2024,
        ratio_2023=ratio_2023,
        nivel_riesgo=nivel_riesgo,
        pagina_fuente=datos['pagina_encontrada'],
        fecha_extraccion=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return metrica


def evaluar_nivel_riesgo(ratio: float) -> str:
    """
    Evalúa el nivel de riesgo basado en el ratio.

    Benchmarks sectoriales Colombia:
    - Bajo: < 4%
    - Medio: 4% - 7%
    - Alto: 7% - 10%
    - Crítico: > 10%

    Parámetros:
    - ratio: valor del ratio (ejemplo: 0.0721 para 7.21%)

    Retorna:
    - String con nivel: "BAJO", "MEDIO", "ALTO", "CRÍTICO"
    """

    if ratio < 0.04:
        return "BAJO"
    elif ratio < 0.07:
        return "MEDIO"
    elif ratio < 0.10:
        return "ALTO"
    else:
        return "CRÍTICO"


# Código de prueba
if __name__ == "__main__":

    ruta = "../data/inputs/bancolombia_2024.pdf"

    print("="*70)
    print("🎯 PRUEBA DE MÉTRICA M001")
    print("="*70 + "\n")

    metrica = extraer_metrica_m001(ruta)

    if metrica:
        print("\n" + "="*70)
        print("✅ EXTRACCIÓN COMPLETA")
        print("="*70)
        print(metrica)

        print("\n" + "="*70)
        print("💾 FORMATO JSON:")
        print("="*70)
        import json
        print(json.dumps(metrica.to_dict(), indent=2, ensure_ascii=False))

    else:
        print("\n❌ La extracción falló")
