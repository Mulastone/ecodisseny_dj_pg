# ⚙️ Asegúrate de que existe la carpeta
mkdir -p maestros/fixtures

# 💾 Exportar cada modelo a JSON (excepto Clients y PersonaContactClient)
python manage.py dumpdata maestros.TipusRecurso --indent 2 > maestros/fixtures/tipusrecurso.json
python manage.py dumpdata maestros.Recurso --indent 2 > maestros/fixtures/recurso.json
python manage.py dumpdata maestros.Parroquia --indent 2 > maestros/fixtures/parroquia.json
python manage.py dumpdata maestros.Poblacio --indent 2 > maestros/fixtures/poblacio.json
python manage.py dumpdata maestros.Ubicacio --indent 2 > maestros/fixtures/ubicacio.json
python manage.py dumpdata maestros.Hores --indent 2 > maestros/fixtures/hores.json
python manage.py dumpdata maestros.Treball --indent 2 > maestros/fixtures/treballs.json
python manage.py dumpdata maestros.Tasca --indent 2 > maestros/fixtures/tasca.json
python manage.py dumpdata maestros.TasquesTreball --indent 2 > maestros/fixtures/tasques_treball.json
python manage.py dumpdata maestros.Desplacament --indent 2 > maestros/fixtures/desplacaments.json
python manage.py dumpdata maestros.DepartamentClient --indent 2 > maestros/fixtures/departament_client.json