# extractors/extraer_todas_metricas.py
"""
EXTRACTOR UNIFICADO - FINSTAT DIAGNOSTIC ENGINE
Ejecuta todas las métricas implementadas en un solo paso.

USO:
    python extraer_todas_metricas.py

OUTPUT:
    output/diagnostico_completo_bancolombia_2024.json
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Importar extractores
from metrica_m001 import extraer_metrica_m001
from metrica_m003 import extraer_metrica_m003
from metrica_m004 import extraer_metrica_m004
from metrica_m005 import extraer_metrica_m005


def extraer_todas_metricas(ruta_pdf: str, banco: str = "bancolombia", año: int = 2024):
    """
    Ejecuta todas las métricas implementadas.

    Returns:
        dict con estructura:
        {
            'metadata': {...},
            'metricas': {
                'M001': {...},
                'M003': {...},
                'M004': {...},
                'M005': {...}
            },
            'validacion': {...}
        }
    """

    print("\n" + "="*70)
    print("🚀 FINSTAT DIAGNOSTIC ENGINE - EXTRACCIÓN COMPLETA")
    print("="*70)
    print(f"📄 PDF: {ruta_pdf}")
    print(f"🏦 Banco: {banco.upper()}")
    print(f"📅 Año: {año}")
    print("="*70 + "\n")

    # Contenedor de resultados
    resultados = {
        'metadata': {
            'banco': banco,
            'año': año,
            'pdf_fuente': ruta_pdf,
            'fecha_procesamiento': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'version_sistema': '1.0.0'
        },
        'metricas': {},
        'validacion': {
            'metricas_exitosas': [],
            'metricas_fallidas': [],
            'coherencia': {}
        }
    }

    # Lista de extractores
    extractores = [
        ('M001', extraer_metrica_m001, 'Provisión/Cartera Total'),
        ('M003', extraer_metrica_m003, 'NPL Ratio'),
        ('M004', extraer_metrica_m004, 'Coverage Ratio'),
        ('M005', extraer_metrica_m005, 'Cartera Riesgosa (C+D+E)')
    ]

    # Ejecutar cada extractor
    for metrica_id, funcion_extractora, nombre in extractores:
        print(f"\n{'─'*70}")
        print(f"📊 Extrayendo {metrica_id}: {nombre}")
        print(f"{'─'*70}")

        try:
            metrica = funcion_extractora(ruta_pdf)

            if metrica:
                resultados['metricas'][metrica_id] = metrica.to_dict()
                resultados['validacion']['metricas_exitosas'].append(metrica_id)
                print(f"✅ {metrica_id} extraída correctamente")
            else:
                resultados['validacion']['metricas_fallidas'].append(metrica_id)
                print(f"❌ {metrica_id} falló en extracción")

        except Exception as e:
            resultados['validacion']['metricas_fallidas'].append(metrica_id)
            print(f"❌ {metrica_id} error: {str(e)}")

    # VALIDACIÓN CRUZADA
    print(f"\n{'='*70}")
    print("🔍 VALIDACIÓN CRUZADA DE COHERENCIA")
    print("="*70)

    validar_coherencia(resultados)

    # RESUMEN FINAL
    print(f"\n{'='*70}")
    print("📋 RESUMEN DE EXTRACCIÓN")
    print("="*70)
    print(f"✅ Métricas exitosas: {len(resultados['validacion']['metricas_exitosas'])}")
    print(f"❌ Métricas fallidas:  {len(resultados['validacion']['metricas_fallidas'])}")

    if resultados['validacion']['metricas_exitosas']:
        print(f"\nMétricas extraídas: {', '.join(resultados['validacion']['metricas_exitosas'])}")

    if resultados['validacion']['metricas_fallidas']:
        print(f"\nMétricas con errores: {', '.join(resultados['validacion']['metricas_fallidas'])}")

    return resultados


def validar_coherencia(resultados):
    """
    Valida que las métricas sean coherentes entre sí.

    REGLAS:
    1. M004_coverage = M001_provision / M003_cartera_vencida
    2. M005_riesgosa > M003_npl (siempre)
    3. M001_ratio entre 1%-20%
    """

    metricas = resultados['metricas']
    validacion = resultados['validacion']['coherencia']

    # Regla 1: Coverage = Provisión / Cartera Vencida
    if 'M001' in metricas and 'M003' in metricas and 'M004' in metricas:

        provision = metricas['M001']['valores']['2024']['provision']
        cartera_vencida = metricas['M003']['valores']['2024']['cartera_vencida']
        coverage_reportado = metricas['M004']['valores']['2024']['coverage_ratio']

        coverage_calculado = provision / cartera_vencida
        diferencia = abs(coverage_calculado - coverage_reportado)

        if diferencia < 0.01:  # Tolerancia 1%
            validacion['coverage_coherente'] = True
            print(f"✅ Coverage coherente: {coverage_reportado:.2%} (diff: {diferencia:.4f})")
        else:
            validacion['coverage_coherente'] = False
            print(f"⚠️  Coverage discrepancia: reportado={coverage_reportado:.2%}, calculado={coverage_calculado:.2%}")

    # Regla 2: Cartera Riesgosa > NPL
    if 'M003' in metricas and 'M005' in metricas:

        npl = metricas['M003']['valores']['2024']['npl_ratio']
        riesgosa = metricas['M005']['valores']['2024']['ratio_riesgosa_cde']

        if riesgosa > npl:
            validacion['riesgosa_mayor_que_npl'] = True
            diferencia_pp = (riesgosa - npl) * 100
            print(f"✅ Cartera riesgosa > NPL: {riesgosa:.2%} > {npl:.2%} (+{diferencia_pp:.2f}pp)")
        else:
            validacion['riesgosa_mayor_que_npl'] = False
            print(f"⚠️  Cartera riesgosa MENOR que NPL (anormal)")

    # Regla 3: Provisión/Cartera en rango razonable
    if 'M001' in metricas:

        ratio = metricas['M001']['valores']['2024']['ratio']

        if 0.01 <= ratio <= 0.20:
            validacion['provision_rango_valido'] = True
            print(f"✅ Provisión/Cartera en rango válido: {ratio:.2%}")
        else:
            validacion['provision_rango_valido'] = False
            print(f"⚠️  Provisión/Cartera fuera de rango esperado: {ratio:.2%}")


def guardar_resultados(resultados, output_dir="../output"):
    """Guarda resultados en JSON."""

    banco = resultados['metadata']['banco']
    año = resultados['metadata']['año']

    # Crear directorio si no existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Guardar JSON completo
    output_path = f"{output_dir}/diagnostico_completo_{banco}_{año}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en: {output_path}")
    return output_path


def generar_resumen_visual(resultados):
    """Genera tabla visual de resultados."""

    print("\n" + "="*70)
    print("📊 TABLA RESUMEN DE MÉTRICAS")
    print("="*70)
    print(f"{'ID':<6} {'Métrica':<30} {'Valor 2024':<12} {'Nivel':<12}")
    print("─"*70)

    metricas = resultados['metricas']

    if 'M001' in metricas:
        m = metricas['M001']
        ratio = m['valores']['2024']['ratio']
        nivel = m['analisis']['nivel_riesgo']
        print(f"{'M001':<6} {'Provisión/Cartera':<30} {ratio:>11.2%} {nivel:<12}")

    if 'M003' in metricas:
        m = metricas['M003']
        npl = m['valores']['2024']['npl_ratio']
        nivel = m['analisis']['nivel_riesgo']
        print(f"{'M003':<6} {'NPL Ratio':<30} {npl:>11.2%} {nivel:<12}")

    if 'M004' in metricas:
        m = metricas['M004']
        cov = m['valores']['2024']['coverage_ratio']
        nivel = m['analisis']['nivel_riesgo']
        print(f"{'M004':<6} {'Coverage Ratio':<30} {cov:>11.2%} {nivel:<12}")

    if 'M005' in metricas:
        m = metricas['M005']
        cde = m['valores']['2024']['ratio_riesgosa_cde']
        nivel = m['analisis']['nivel_riesgo']
        print(f"{'M005':<6} {'Cartera Riesgosa (C+D+E)':<30} {cde:>11.2%} {nivel:<12}")

    print("="*70)


# ═══════════════════════════════════════════════════════════════════════
# CÓDIGO DE PRUEBA
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # Ruta del PDF
    ruta_pdf = "../data/inputs/bancolombia_2024.pdf"

    # Ejecutar extracción completa
    resultados = extraer_todas_metricas(ruta_pdf)

    # Guardar resultados
    guardar_resultados(resultados)

    # Mostrar resumen visual
    generar_resumen_visual(resultados)

    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print("\nPróximos pasos:")
    print("1. Revisar: output/diagnostico_completo_bancolombia_2024.json")
    print("2. Agregar más métricas (M006-M015)")
    print("3. Crear generador de reportes Word")
