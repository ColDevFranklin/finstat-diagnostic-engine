# extractors/metrica_m003.py
# Métrica M003: NPL Ratio - VERSIÓN FINAL con datos reales

import sys
sys.path.append('..')

from parsers.extraer_desde_pagina_95 import (
    extraer_cobertura_vencida,
    calcular_cartera_vencida_desde_cobertura
)
from parsers.extraer_tabla_inteligente import extraer_tabla_provision
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


@dataclass
class MetricaM003:
    """
    M003: NPL Ratio (Non-Performing Loans)

    Calculado indirectamente usando:
    Cartera Vencida = Provisión Total / Coverage Ratio
    NPL Ratio = Cartera Vencida / Cartera Total

    Interpretación:
    - < 3%: EXCELENTE
    - 3-5%: BUENO
    - 5-8%: ACEPTABLE
    - 8-12%: ALTO
    - > 12%: CRÍTICO
    """

    # Valores (sin defaults)
    cartera_vencida_2024: float
    cartera_vencida_2023: float
    cartera_total_2024: float
    cartera_total_2023: float
    npl_ratio_2024: float
    npl_ratio_2023: float
    calidad_cartera: str

    # Datos intermedios
    provision_2024: float
    provision_2023: float
    coverage_2024: float
    coverage_2023: float

    # Metadata
    pagina_fuente: int
    fecha_extraccion: str

    # Identificación (con defaults)
    id: str = "M003"
    nombre: str = "NPL Ratio"
    cambio_yoy: float = 0.0
    cambio_absoluto_vencida: float = 0.0

    def __post_init__(self):
        """Calcular cambios YoY."""
        self.cambio_yoy = self.npl_ratio_2024 - self.npl_ratio_2023
        self.cambio_absoluto_vencida = (
            self.cartera_vencida_2024 - self.cartera_vencida_2023
        )

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'valores': {
                '2024': {
                    'cartera_vencida': self.cartera_vencida_2024,
                    'cartera_total': self.cartera_total_2024,
                    'npl_ratio': self.npl_ratio_2024
                },
                '2023': {
                    'cartera_vencida': self.cartera_vencida_2023,
                    'cartera_total': self.cartera_total_2023,
                    'npl_ratio': self.npl_ratio_2023
                }
            },
            'analisis': {
                'cambio_yoy_pp': self.cambio_yoy,
                'cambio_vencida_monto': self.cambio_absoluto_vencida,
                'calidad_cartera': self.calidad_cartera
            },
            'calculo': {
                'metodo': 'indirecto',
                'fuente': 'Provisión / Coverage Ratio',
                'provision_2024': self.provision_2024,
                'coverage_2024': self.coverage_2024
            },
            'metadata': {
                'pagina_fuente': self.pagina_fuente,
                'fecha_extraccion': self.fecha_extraccion
            }
        }

    def __str__(self):
        """Representación legible."""

        # Símbolo de tendencia
        if self.cambio_yoy > 0:
            simbolo = "↑"
            texto_cambio = f"Incremento de {abs(self.cambio_yoy*100):.2f} pp"
            color = "🔴"  # Malo si sube NPL
        elif self.cambio_yoy < 0:
            simbolo = "↓"
            texto_cambio = f"Reducción de {abs(self.cambio_yoy*100):.2f} pp"
            color = "🟢"  # Bueno si baja NPL
        else:
            simbolo = "→"
            texto_cambio = "Sin cambio"
            color = "⚪"

        # Emoji por nivel
        emoji = {
            "EXCELENTE": "🌟",
            "BUENO": "✅",
            "ACEPTABLE": "⚠️",
            "ALTO": "🟠",
            "CRÍTICO": "🚨"
        }

        return f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.id}: {self.nombre:<48} ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 VALORES 2024:                                            ║
║     Cartera Vencida:  ${self.cartera_vencida_2024:>15,.0f} millones  ║
║     Cartera Total:    ${self.cartera_total_2024:>15,.0f} millones  ║
║     NPL Ratio:        {self.npl_ratio_2024:>20.2%}                    ║
║                                                              ║
║  📊 VALORES 2023:                                            ║
║     Cartera Vencida:  ${self.cartera_vencida_2023:>15,.0f} millones  ║
║     Cartera Total:    ${self.cartera_total_2023:>15,.0f} millones  ║
║     NPL Ratio:        {self.npl_ratio_2023:>20.2%}                    ║
║                                                              ║
║  📈 EVOLUCIÓN YoY:                                           ║
║     {simbolo} {texto_cambio:<56} {color}║
║     Monto vencida: ${self.cambio_absoluto_vencida:>15,.0f} millones  ║
║                                                              ║
║  🔬 MÉTODO DE CÁLCULO:                                       ║
║     Indirecto (Provisión / Coverage Ratio)                  ║
║     Coverage 2024: {self.coverage_2024:>15.2%}                       ║
║                                                              ║
║  🎯 CALIDAD DE CARTERA: {self.calidad_cartera:<20} {emoji.get(self.calidad_cartera, '❓'):<11}║
║                                                              ║
║  📄 Fuente: Página {self.pagina_fuente:<44} ║
║  📅 Fecha: {self.fecha_extraccion:<45} ║
╚══════════════════════════════════════════════════════════════╝
        """


def extraer_metrica_m003(ruta_pdf: str) -> Optional[MetricaM003]:
    """
    Extrae y calcula M003: NPL Ratio.

    Proceso:
    1. Extrae Provisión y Cartera Total (reutiliza M001)
    2. Extrae Coverage Ratio de página 95
    3. Calcula Cartera Vencida = Provisión / Coverage
    4. Calcula NPL Ratio = Cartera Vencida / Cartera Total
    """

    print("🚀 Extrayendo Métrica M003: NPL Ratio")
    print("=" * 70)

    # PASO 1: Obtener Provisión y Cartera Total (de M001)
    print("\n📊 PASO 1: Extrayendo Provisión y Cartera Total...")
    datos_provision = extraer_tabla_provision(ruta_pdf)

    if not datos_provision or not datos_provision['provision_2024']:
        print("❌ No se pudo extraer provisión y cartera")
        return None

    provision_2024 = datos_provision['provision_2024']
    provision_2023 = datos_provision['provision_2023']
    cartera_total_2024 = datos_provision['cartera_2024']
    cartera_total_2023 = datos_provision['cartera_2023']

    print(f"✅ Provisión 2024: ${provision_2024:,.0f}")
    print(f"✅ Cartera Total 2024: ${cartera_total_2024:,.0f}")

    # PASO 2: Obtener Coverage Ratio
    print("\n📊 PASO 2: Extrayendo Coverage Ratio...")
    datos_coverage = extraer_cobertura_vencida(ruta_pdf)

    if not datos_coverage or not datos_coverage['cobertura_2024']:
        print("❌ No se pudo extraer coverage ratio")
        return None

    coverage_2024 = datos_coverage['cobertura_2024']
    coverage_2023 = datos_coverage['cobertura_2023']

    print(f"✅ Coverage 2024: {coverage_2024:.2%}")
    print(f"✅ Coverage 2023: {coverage_2023:.2%}")

    # PASO 3: Calcular Cartera Vencida
    print("\n📊 PASO 3: Calculando Cartera Vencida...")
    cartera_vencida_2024 = calcular_cartera_vencida_desde_cobertura(
        provision_2024, coverage_2024
    )
    cartera_vencida_2023 = calcular_cartera_vencida_desde_cobertura(
        provision_2023, coverage_2023
    )

    print(f"✅ Cartera Vencida 2024: ${cartera_vencida_2024:,.0f}")
    print(f"   (Cálculo: ${provision_2024:,.0f} / {coverage_2024:.2%})")

    # PASO 4: Calcular NPL Ratio
    print("\n📊 PASO 4: Calculando NPL Ratio...")
    npl_2024 = cartera_vencida_2024 / cartera_total_2024
    npl_2023 = cartera_vencida_2023 / cartera_total_2023

    print(f"✅ NPL Ratio 2024: {npl_2024:.2%}")
    print(f"✅ NPL Ratio 2023: {npl_2023:.2%}")

    # PASO 5: Evaluar calidad
    calidad = evaluar_calidad_cartera(npl_2024)
    print(f"\n🎯 Calidad de cartera: {calidad}")

    # Crear métrica
    metrica = MetricaM003(
        cartera_vencida_2024=cartera_vencida_2024,
        cartera_vencida_2023=cartera_vencida_2023,
        cartera_total_2024=cartera_total_2024,
        cartera_total_2023=cartera_total_2023,
        npl_ratio_2024=npl_2024,
        npl_ratio_2023=npl_2023,
        calidad_cartera=calidad,
        provision_2024=provision_2024,
        provision_2023=provision_2023,
        coverage_2024=coverage_2024,
        coverage_2023=coverage_2023,
        pagina_fuente=datos_coverage['pagina_encontrada'],
        fecha_extraccion=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return metrica


def evaluar_calidad_cartera(npl_ratio: float) -> str:
    """Evalúa calidad de cartera basado en NPL ratio."""
    if npl_ratio < 0.03:
        return "EXCELENTE"
    elif npl_ratio < 0.05:
        return "BUENO"
    elif npl_ratio < 0.08:
        return "ACEPTABLE"
    elif npl_ratio < 0.12:
        return "ALTO"
    else:
        return "CRÍTICO"


# CÓDIGO DE PRUEBA
if __name__ == "__main__":

    ruta = "../data/inputs/bancolombia_2024.pdf"

    print("=" * 70)
    print("🎯 PRUEBA DE MÉTRICA M003")
    print("=" * 70 + "\n")

    metrica = extraer_metrica_m003(ruta)

    if metrica:
        print("\n" + "=" * 70)
        print("✅ EXTRACCIÓN COMPLETA")
        print("=" * 70)
        print(metrica)

        print("\n" + "=" * 70)
        print("💾 FORMATO JSON:")
        print("=" * 70)
        print(json.dumps(metrica.to_dict(), indent=2, ensure_ascii=False))

        # Guardar en archivo
        output_path = "../output/metrica_m003_bancolombia_2024.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrica.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n✅ Guardado en: {output_path}")
    else:
        print("\n❌ La extracción falló")
