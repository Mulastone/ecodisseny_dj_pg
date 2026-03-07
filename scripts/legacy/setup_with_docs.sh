#!/bin/bash

# Script completo de configuración con documentación
# Incluye base de datos, fixtures y documentación

set -e  # Salir si cualquier comando falla

echo "🚀 Iniciando configuración completa de Ecodisseny..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
function echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

function echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo_error "Este script debe ejecutarse desde el directorio raíz del proyecto Django"
    exit 1
fi

# 1. Verificar/crear virtual environment
echo_info "Verificando entorno virtual..."
if [ ! -d "venv_postgres" ]; then
    echo_info "Creando entorno virtual..."
    python3 -m venv venv_postgres
    echo_success "Entorno virtual creado"
fi

# 2. Activar entorno virtual
echo_info "Activando entorno virtual..."
source venv_postgres/bin/activate
echo_success "Entorno virtual activado"

# 3. Instalar dependencias
echo_info "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
echo_success "Dependencias instaladas"

# 4. Verificar PostgreSQL
echo_info "Verificando conexión a PostgreSQL..."
if ! python manage.py check --database default; then
    echo_error "No se puede conectar a PostgreSQL. Asegúrate de que esté ejecutándose."
    echo_info "Para Docker: docker-compose up -d db"
    exit 1
fi
echo_success "Conexión a PostgreSQL verificada"

# 5. Ejecutar migraciones
echo_info "Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate
echo_success "Migraciones aplicadas"

# 6. Cargar fixtures
echo_info "Cargando datos iniciales (fixtures)..."
if [ -f "load_fixtures.sh" ]; then
    chmod +x load_fixtures.sh
    ./load_fixtures.sh
    echo_success "Fixtures cargados"
else
    echo_warning "Script load_fixtures.sh no encontrado, saltando..."
fi

# 7. Crear superusuario si no existe
echo_info "Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@ecodisseny.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('ℹ️  Superusuario ya existe')
"

# 8. Cargar documentación
echo_info "Cargando documentación..."
python manage.py cargar_documentacion --update
echo_success "Documentación cargada"

# 9. Limpiar documentos huérfanos
echo_info "Limpiando documentos huérfanos..."
python manage.py limpiar_documentos
echo_success "Limpieza de documentos completada"

# 10. Recopilar archivos estáticos (si es necesario)
echo_info "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --verbosity 0
echo_success "Archivos estáticos recopilados"

# 11. Información final
echo ""
echo_success "🎉 ¡Configuración completada exitosamente!"
echo ""
echo_info "📋 Resumen de lo que se ha configurado:"
echo "   • Base de datos migrada"
echo "   • Datos iniciales cargados (fixtures)"
echo "   • Documentación cargada automáticamente"
echo "   • Superusuario disponible (si no existía)"
echo "   • Archivos estáticos recopilados"
echo ""
echo_info "🚀 Para iniciar el servidor de desarrollo:"
echo "   python manage.py runserver"
echo ""
echo_info "🌐 Para acceder a la aplicación:"
echo "   • Aplicación: http://localhost:8000/"
echo "   • Admin: http://localhost:8000/admin/"
echo "   • Documentación: http://localhost:8000/documentacion/"
echo ""
echo_info "👤 Credenciales de administrador (si se creó):"
echo "   • Usuario: admin"
echo "   • Contraseña: admin123"
echo ""
