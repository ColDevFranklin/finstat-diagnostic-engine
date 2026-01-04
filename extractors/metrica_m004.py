# extractors/metrica_m004.py
# Métrica M004: Coverage Ratio

import sys
sys.path.append('..')

from parsers.extraer_desde_pagina_95 import extraer_cobertura_vencida
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


@dataclass
class MetricaM004:
    """
    M004: Coverage Ratio (Cobertura de Cartera Vencida)

    Mide qué tan bien provisionada está la cartera vencida.

    Fórmula: Provisión Total / Cartera Vencida

    Interpretación:
    - > 150%: CONSERVADOR (sobre-provisionado)
    - 100-150%: ADECUADO
    - 80-100%: LÍMITE
    - < 80%: INSUFICIENTE (riesgo)
    """

    # Valores (sin defaults)
    coverage_2024: float
    coverage_2023: float
    nivel_cobertura: str
    pagina_fuente: int
    fecha_extraccion: str

    # Identificación (con defaults)
    id: str = "M004"
    nombre: str = "Coverage Ratio"
    cambio_yoy: float = 0.0

    def __post_init__(self):
        """Calcular cambio YoY."""
        self.cambio_yoy = self.coverage_2024 - self.coverage_2023

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'valores': {
                '2024': {
                    'coverage_ratio': self.coverage_2024
                },
                '2023': {
                    'coverage_ratio': self.coverage_2023
                }
            },
            'analisis': {
                'cambio_yoy_pp': self.cambio_yoy,
                'nivel_cobertura': self.nivel_cobertura
            },
            'interpretacion': {
                'significado': f'La provisión cubre {self.coverage_2024:.0%} de la cartera vencida',
                'implicacion': obtener_implicacion(self.nivel_cobertura)
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
            color = "🟢"  # Bueno si sube coverage
        elif self.cambio_yoy < 0:
            simbolo = "↓"
            texto_cambio = f"Reducción de {abs(self.cambio_yoy*100):.2f} pp"
            color = "🔴"  # Malo si baja coverage
        else:
            simbolo = "→"
            texto_cambio = "Sin cambio"
            color = "⚪"

        # Emoji por nivel
        emoji = {
            "CONSERVADOR": "✅",
            "ADECUADO": "✅",
            "LÍMITE": "⚠️",
            "INSUFICIENTE": "🚨"
        }

        return f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.id}: {self.nombre:<48} ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 COVERAGE RATIO (Provisión/Cartera Vencida):              ║
║                                                              ║
║     2024: {self.coverage_2024:>20.2%}                                 ║
║     2023: {self.coverage_2023:>20.2%}                                 ║
║                                                              ║
║  📈 EVOLUCIÓN YoY:                                           ║
║     {simbolo} {texto_cambio:<56} {color}║
║                                                              ║
║  🎯 NIVEL DE COBERTURA: {self.nivel_cobertura:<20} {emoji.get(self.nivel_cobertura, '❓'):<11}║
║                                                              ║
║  💡 INTERPRETACIÓN:                                          ║
║     La provisión cubre {self.coverage_2024:.0%} de la cartera vencida.      ║
║     {obtener_implicacion(self.nivel_cobertura):<59}║
║                                                              ║
║  📄 Fuente: Página {self.pagina_fuente:<44} ║
║  📅 Fecha: {self.fecha_extraccion:<45} ║
╚══════════════════════════════════════════════════════════════╝
        """


def extraer_metrica_m004(ruta_pdf: str) -> Optional[MetricaM004]:
    """Extrae M004: Coverage Ratio."""

    print("🚀 Extrayendo Métrica M004: Coverage Ratio")
    print("=" * 70)

    datos = extraer_cobertura_vencida(ruta_pdf)

    if not datos or not datos['cobertura_2024']:
        print("❌ No se pudo extraer coverage ratio")
        return None

    print(f"\n✅ Coverage 2024: {datos['cobertura_2024']:.2%}")
    print(f"✅ Coverage 2023: {datos['cobertura_2023']:.2%}")

    # Evaluar nivel
    nivel = evaluar_nivel_cobertura(datos['cobertura_2024'])
    print(f"\n🎯 Nivel de cobertura: {nivel}")

    metrica = MetricaM004(
        coverage_2024=datos['cobertura_2024'],
        coverage_2023=datos['cobertura_2023'],
        nivel_cobertura=nivel,
        pagina_fuente=datos['pagina_encontrada'],
        fecha_extraccion=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return metrica


def evaluar_nivel_cobertura(coverage: float) -> str:
    """Evalúa nivel de cobertura."""
    if coverage > 1.50:
        return "CONSERVADOR"
    elif coverage >= 1.00:
        return "ADECUADO"
    elif coverage >= 0.80:
        return "LÍMITE"
    else:
        return "INSUFICIENTE"


def obtener_implicacion(nivel: str) -> str:
    """Retorna la implicación del nivel de cobertura."""
    implicaciones = {
        "CONSERVADOR": "Provisión sobrada, postura conservadora.",
        "ADECUADO": "Provisión suficiente para cubrir pérdidas.",
        "LÍMITE": "Provisión justa, poco margen de seguridad.",
        "INSUFICIENTE": "Provisión insuficiente, riesgo de pérdidas."
    }
    return implicaciones.get(nivel, "Nivel desconocido")


# CÓDIGO DE PRUEBA
if __name__ == "__main__":

    ruta = "../data/inputs/bancolombia_2024.pdf"

    print("=" * 70)
    print("🎯 PRUEBA DE MÉTRICA M004")
    print("=" * 70 + "\n")

    metrica = extraer_metrica_m004(ruta)

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
        output_path = "../output/metrica_m004_bancolombia_2024.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrica.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n✅ Guardado en: {output_path}")
    else:
        print("\n❌ La extracción falló")
