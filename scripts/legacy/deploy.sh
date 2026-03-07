#!/bin/bash

# Script de despliegue para producción
# Ejecutar en el VPS como: ./deploy.sh

set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue de Ecodisseny..."

# Verificar que estamos en la rama correcta
if [ "$(git branch --show-current)" != "docker" ]; then
    echo "❌ Error: Debes estar en la rama 'docker'"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Error: Debes crear el archivo .env basado en .env.example"
    echo "   cp .env.example .env"
    echo "   nano .env  # Editar con tus datos"
    exit 1
fi

# Hacer pull de los últimos cambios
echo "📥 Descargando últimos cambios..."
git pull origin docker

# Parar contenedores si están ejecutándose
echo "🛑 Parando contenedores existentes..."
docker-compose -f docker-compose.prod.yml down

# Construir y levantar en producción
echo "🔨 Construyendo contenedores..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Levantando aplicación..."
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que la aplicación esté lista
echo "⏳ Esperando que la aplicación esté lista..."
sleep 30

# Verificar que todo esté funcionando
echo "🔍 Verificando servicios..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ ¡Despliegue completado!"
echo "🌐 Tu aplicación está disponible en: https://$(grep DOMAIN_NAME .env | cut -d'=' -f2)"
echo "📊 Para ver logs: docker-compose -f docker-compose.prod.yml logs -f"
