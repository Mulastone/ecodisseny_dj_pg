#!/bin/bash

echo "📦 Generando fixtures para datos maestros..."

# ⚙️ Asegúrate de que existe la carpeta
mkdir -p maestros/fixtures

echo "💾 Exportando modelos a JSON..."

# 💾 Exportar cada modelo a JSON (excepto Clients y PersonaContactClient)
python manage.py dumpdata maestros.TipusRecurso --indent 2 > maestros/fixtures/tipusrecurso.json
echo "  ✓ tipusrecurso.json"

python manage.py dumpdata maestros.Recurso --indent 2 > maestros/fixtures/recurso.json
echo "  ✓ recurso.json"

python manage.py dumpdata maestros.Parroquia --indent 2 > maestros/fixtures/parroquia.json
echo "  ✓ parroquia.json"

python manage.py dumpdata maestros.Poblacio --indent 2 > maestros/fixtures/poblacio.json
echo "  ✓ poblacio.json"

python manage.py dumpdata maestros.Ubicacio --indent 2 > maestros/fixtures/ubicacio.json
echo "  ✓ ubicacio.json"

python manage.py dumpdata maestros.Hores --indent 2 > maestros/fixtures/hores.json
echo "  ✓ hores.json"

python manage.py dumpdata maestros.Treball --indent 2 > maestros/fixtures/treballs.json
echo "  ✓ treballs.json"

python manage.py dumpdata maestros.Tasca --indent 2 > maestros/fixtures/tasca.json
echo "  ✓ tasca.json"

python manage.py dumpdata maestros.TasquesTreball --indent 2 > maestros/fixtures/tasques_treball.json
echo "  ✓ tasques_treball.json"

python manage.py dumpdata maestros.Desplacament --indent 2 > maestros/fixtures/desplacaments.json
echo "  ✓ desplacaments.json"

python manage.py dumpdata maestros.DepartamentClient --indent 2 > maestros/fixtures/departament_client.json
echo "  ✓ departament_client.json"

echo ""
echo "✅ Fixtures generados en maestros/fixtures/"
echo "   Para cargarlos: ./load_fixtures.sh"