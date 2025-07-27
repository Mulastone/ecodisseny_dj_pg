# 1. Borrar el entorno actual
rm -rf venv_postgres

# 2. Crear nuevo entorno
python3 -m venv venv_postgres

# 3. Activarlo
source venv_postgres/bin/activate

# 4. Instalar tus dependencias (puede ser desde tu requirements.txt)
pip install -r requirements.txt
