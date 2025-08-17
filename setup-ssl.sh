#!/bin/bash

# Script para generar certificados SSL
# Ejecutar DESPUÉS del primer despliegue

DOMAIN=$(grep DOMAIN_NAME .env | cut -d'=' -f2)
EMAIL=$(grep EMAIL .env | cut -d'=' -f2)

echo "🔒 Generando certificados SSL para $DOMAIN..."

# Reemplazar dominio en nginx
sed -i "s/tudominio.com/$DOMAIN/g" nginx/default.conf

# Generar certificado
docker-compose -f docker-compose.prod.yml run --rm certbot

# Recargar nginx
docker-compose -f docker-compose.prod.yml restart nginx

echo "✅ Certificados SSL generados!"
echo "🔄 Reiniciando servicios..."

# Verificar que todo funciona
docker-compose -f docker-compose.prod.yml ps

echo "🌐 Tu sitio con HTTPS está disponible en: https://$DOMAIN"
