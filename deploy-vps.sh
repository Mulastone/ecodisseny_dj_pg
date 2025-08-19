#!/bin/bash

# 🚀 Script de despliegue para VPS con Docker + Nginx nativo
# Uso: ./deploy-vps.sh

set -e

echo "🚀 Iniciando despliegue en VPS..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encuentra docker-compose.yml. Ejecuta desde el directorio del proyecto."
    exit 1
fi

# 1. Actualizar código
print_status "Actualizando código desde Git..."
git pull origin docker

# 2. Parar servicios Docker existentes
print_status "Parando contenedores existentes..."
docker-compose down

# 3. Construir nueva imagen
print_status "Construyendo nueva imagen Docker..."
docker-compose build --no-cache web

# 4. Iniciar servicios
print_status "Iniciando servicios Docker..."
docker-compose up -d

# 5. Esperar a que la aplicación esté lista
print_status "Esperando que la aplicación esté lista..."
sleep 30

# Verificar que los contenedores están funcionando
if docker-compose ps | grep -q "Up"; then
    print_success "Contenedores Docker iniciados correctamente"
else
    print_error "Error al iniciar contenedores Docker"
    docker-compose logs
    exit 1
fi

# 6. Configurar Nginx si es la primera vez
if [ ! -f "/etc/nginx/sites-available/app.arasmu.net" ]; then
    print_status "Configurando Nginx por primera vez..."
    
    # Copiar configuración
    sudo cp nginx/vps-app.arasmu.net.conf /etc/nginx/sites-available/app.arasmu.net
    
    # Habilitar sitio
    sudo ln -sf /etc/nginx/sites-available/app.arasmu.net /etc/nginx/sites-enabled/
    
    # Deshabilitar sitio por defecto
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Verificar configuración
    if sudo nginx -t; then
        print_success "Configuración de Nginx válida"
        sudo systemctl reload nginx
    else
        print_error "Error en configuración de Nginx"
        exit 1
    fi
else
    print_status "Recargando configuración de Nginx..."
    sudo systemctl reload nginx
fi

# 7. Verificar que la aplicación responde
print_status "Verificando que la aplicación responde..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|302"; then
    print_success "Aplicación Django funcionando correctamente"
else
    print_warning "La aplicación puede tardar un poco más en estar lista"
fi

# 8. Mostrar estado final
print_status "Estado final del despliegue:"
echo ""
docker-compose ps
echo ""

print_success "🎉 Despliegue completado!"
echo ""
echo "📍 URLs disponibles:"
echo "   • HTTP:  http://161.97.147.142"
echo "   • HTTPS: https://app.arasmu.net (después de configurar SSL)"
echo ""
echo "🔧 Próximos pasos:"
echo "   1. Configurar DNS: app.arasmu.net → 161.97.147.142"
echo "   2. Generar SSL: sudo certbot --nginx -d app.arasmu.net"
echo ""
echo "📊 Para monitorear:"
echo "   • Logs Django: docker-compose logs -f web"
echo "   • Logs Nginx: sudo tail -f /var/log/nginx/app.arasmu.net.error.log"
echo "   • Estado: docker-compose ps"
