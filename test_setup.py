# test_setup.py
# Este código verifica que todo está instalado correctamente

import sys
print("✅ Python funciona!")
print(f"Versión: {sys.version}")

try:
    import pdfplumber
    print("✅ pdfplumber instalado")
except:
    print("❌ pdfplumber NO instalado")

try:
    import pandas
    print("✅ pandas instalado")
except:
    print("❌ pandas NO instalado")

try:
    from docx import Document
    print("✅ python-docx instalado")
except:
    print("❌ python-docx NO instalado")

print("\n🎉 Si ves 4 ✅, todo está listo para continuar")
