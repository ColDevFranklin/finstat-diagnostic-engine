# extractors/metrica_m005.py
# Métrica M005: Cartera Riesgosa (C+D+E)

import sys
sys.path.append('..')

from parsers.extraer_calificacion_riesgo import extraer_calificacion_riesgo
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


@dataclass
class MetricaM005:
    """
    M005: Cartera Riesgosa (Categorías C+D+E)

    Mide el porcentaje de cartera en categorías de alto riesgo,
    que son préstamos con alta probabilidad de convertirse en NPL.

    Categorías:
    - A: Riesgo Normal
    - B: Riesgo Aceptable
    - C: Riesgo Apreciable     ← INICIO ZONA RIESGOSA
    - D: Riesgo Significativo  ← ZONA RIESGOSA
    - E: Incobrable            ← ZONA RIESGOSA

    Interpretación:
    - < 3%: EXCELENTE
    - 3-5%: BUENO
    - 5-8%: ACEPTABLE
    - 8-12%: ALTO
    - > 12%: CRÍTICO
    """

    # Valores totales
    cartera_a_2024: float
    cartera_b_2024: float
    cartera_c_2024: float
    cartera_d_2024: float
    cartera_e_2024: float
    cartera_total_2024: float

    cartera_a_2023: float
    cartera_b_2023: float
    cartera_c_2023: float
    cartera_d_2023: float
    cartera_e_2023: float
    cartera_total_2023: float

    # Ratios calculados
    ratio_riesgosa_2024: float  # (C+D+E) / Total
    ratio_riesgosa_2023: float

    # Análisis
    nivel_riesgo: str
    pagina_fuente: int
    fecha_extraccion: str

    # Identificación
    id: str = "M005"
    nombre: str = "Cartera Riesgosa (C+D+E)"
    cambio_yoy: float = 0.0

    def __post_init__(self):
        """Calcular cambio YoY."""
        self.cambio_yoy = self.ratio_riesgosa_2024 - self.ratio_riesgosa_2023

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'valores': {
                '2024': {
                    'categoria_a': self.cartera_a_2024,
                    'categoria_b': self.cartera_b_2024,
                    'categoria_c': self.cartera_c_2024,
                    'categoria_d': self.cartera_d_2024,
                    'categoria_e': self.cartera_e_2024,
                    'total': self.cartera_total_2024,
                    'ratio_riesgosa_cde': self.ratio_riesgosa_2024
                },
                '2023': {
                    'categoria_a': self.cartera_a_2023,
                    'categoria_b': self.cartera_b_2023,
                    'categoria_c': self.cartera_c_2023,
                    'categoria_d': self.cartera_d_2023,
                    'categoria_e': self.cartera_e_2023,
                    'total': self.cartera_total_2023,
                    'ratio_riesgosa_cde': self.ratio_riesgosa_2023
                }
            },
            'analisis': {
                'cambio_yoy_pp': self.cambio_yoy,
                'nivel_riesgo': self.nivel_riesgo
            },
            'composicion_2024': {
                'a_pct': self.cartera_a_2024 / self.cartera_total_2024,
                'b_pct': self.cartera_b_2024 / self.cartera_total_2024,
                'c_pct': self.cartera_c_2024 / self.cartera_total_2024,
                'd_pct': self.cartera_d_2024 / self.cartera_total_2024,
                'e_pct': self.cartera_e_2024 / self.cartera_total_2024
            },
            'metadata': {
                'pagina_fuente': self.pagina_fuente,
                'fecha_extraccion': self.fecha_extraccion
            }
        }

    def __str__(self):
        """Representación legible."""

        # Tendencia
        if self.cambio_yoy > 0:
            simbolo = "↑"
            texto = f"Incremento de {abs(self.cambio_yoy*100):.2f} pp"
            color = "🔴"  # Malo si sube cartera riesgosa
        elif self.cambio_yoy < 0:
            simbolo = "↓"
            texto = f"Reducción de {abs(self.cambio_yoy*100):.2f} pp"
            color = "🟢"  # Bueno si baja
        else:
            simbolo = "→"
            texto = "Sin cambio"
            color = "⚪"

        # Emoji
        emoji = {
            "EXCELENTE": "🌟",
            "BUENO": "✅",
            "ACEPTABLE": "⚠️",
            "ALTO": "🟠",
            "CRÍTICO": "🚨"
        }

        # Calcular porcentajes por categoría
        pct_a = self.cartera_a_2024 / self.cartera_total_2024
        pct_b = self.cartera_b_2024 / self.cartera_total_2024
        pct_c = self.cartera_c_2024 / self.cartera_total_2024
        pct_d = self.cartera_d_2024 / self.cartera_total_2024
        pct_e = self.cartera_e_2024 / self.cartera_total_2024

        return f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.id}: {self.nombre:<40} ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 DISTRIBUCIÓN POR CATEGORÍA (2024):                       ║
║                                                              ║
║     A - Riesgo Normal:        {pct_a:>6.2%}  (${self.cartera_a_2024:>12,.0f})    ║
║     B - Riesgo Aceptable:     {pct_b:>6.2%}  (${self.cartera_b_2024:>12,.0f})    ║
║     ─────────────────────────────────────────────────────   ║
║     C - Riesgo Apreciable:    {pct_c:>6.2%}  (${self.cartera_c_2024:>12,.0f})    ║
║     D - Riesgo Significativo: {pct_d:>6.2%}  (${self.cartera_d_2024:>12,.0f})    ║
║     E - Incobrable:           {pct_e:>6.2%}  (${self.cartera_e_2024:>12,.0f})    ║
║                                                              ║
║  📈 CARTERA RIESGOSA (C+D+E):                                ║
║                                                              ║
║     2024: {self.ratio_riesgosa_2024:>20.2%}                           ║
║     2023: {self.ratio_riesgosa_2023:>20.2%}                           ║
║                                                              ║
║  📈 EVOLUCIÓN YoY:                                           ║
║     {simbolo} {texto:<56} {color}║
║                                                              ║
║  🎯 NIVEL DE RIESGO: {self.nivel_riesgo:<20} {emoji.get(self.nivel_riesgo, '❓'):<11}║
║                                                              ║
║  💡 INTERPRETACIÓN:                                          ║
║     {self.ratio_riesgosa_2024:.1%} de la cartera está en categorías riesgosas ║
║     (C+D+E = alta probabilidad de convertirse en NPL)       ║
║                                                              ║
║  📄 Fuente: Página {self.pagina_fuente:<44} ║
║  📅 Fecha: {self.fecha_extraccion:<45} ║
╚══════════════════════════════════════════════════════════════╝
        """


def evaluar_nivel_riesgo(ratio: float) -> str:
    """Evalúa nivel de riesgo basado en cartera riesgosa."""
    if ratio < 0.03:
        return "EXCELENTE"
    elif ratio < 0.05:
        return "BUENO"
    elif ratio < 0.08:
        return "ACEPTABLE"
    elif ratio < 0.12:
        return "ALTO"
    else:
        return "CRÍTICO"


def extraer_metrica_m005(ruta_pdf: str) -> Optional[MetricaM005]:
    """
    Extrae M005: Cartera Riesgosa (C+D+E).

    Args:
        ruta_pdf: Ruta al archivo PDF bancario

    Returns:
        MetricaM005 o None si falla
    """

    print("🚀 Extrayendo Métrica M005: Cartera Riesgosa (C+D+E)")
    print("=" * 70)

    # Extraer datos usando parser
    datos = extraer_calificacion_riesgo(ruta_pdf)

    if not datos or not datos.get('a_2024'):
        print("❌ No se pudo extraer distribución de cartera")
        return None

    # Calcular ratios riesgosos
    riesgosa_2024 = datos['c_2024'] + datos['d_2024'] + datos['e_2024']
    ratio_2024 = riesgosa_2024 / datos['total_2024']

    riesgosa_2023 = datos['c_2023'] + datos['d_2023'] + datos['e_2023']
    ratio_2023 = riesgosa_2023 / datos['total_2023']

    print(f"\n✅ Cartera Riesgosa 2024: ${riesgosa_2024:,.0f} ({ratio_2024:.2%})")
    print(f"✅ Cartera Riesgosa 2023: ${riesgosa_2023:,.0f} ({ratio_2023:.2%})")

    # Evaluar nivel
    nivel = evaluar_nivel_riesgo(ratio_2024)
    print(f"\n🎯 Nivel de riesgo: {nivel}")

    # Crear objeto métrica
    metrica = MetricaM005(
        cartera_a_2024=datos['a_2024'],
        cartera_b_2024=datos['b_2024'],
        cartera_c_2024=datos['c_2024'],
        cartera_d_2024=datos['d_2024'],
        cartera_e_2024=datos['e_2024'],
        cartera_total_2024=datos['total_2024'],

        cartera_a_2023=datos['a_2023'],
        cartera_b_2023=datos['b_2023'],
        cartera_c_2023=datos['c_2023'],
        cartera_d_2023=datos['d_2023'],
        cartera_e_2023=datos['e_2023'],
        cartera_total_2023=datos['total_2023'],

        ratio_riesgosa_2024=ratio_2024,
        ratio_riesgosa_2023=ratio_2023,

        nivel_riesgo=nivel,
        pagina_fuente=datos.get('pagina_encontrada', 0),
        fecha_extraccion=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return metrica


# CÓDIGO DE PRUEBA
if __name__ == "__main__":

    ruta = "../data/inputs/bancolombia_2024.pdf"

    print("=" * 70)
    print("🎯 PRUEBA DE MÉTRICA M005")
    print("=" * 70 + "\n")

    metrica = extraer_metrica_m005(ruta)

    if metrica:
        print("\n" + "=" * 70)
        print("✅ EXTRACCIÓN COMPLETA")
        print("=" * 70)
        print(metrica)

        print("\n" + "=" * 70)
        print("💾 FORMATO JSON:")
        print("=" * 70)
        print(json.dumps(metrica.to_dict(), indent=2, ensure_ascii=False))

        # Guardar
        output_path = "../output/metrica_m005_bancolombia_2024.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrica.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n✅ Guardado en: {output_path}")
    else:
        print("\n❌ La extracción falló")
