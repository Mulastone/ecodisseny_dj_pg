#!/bin/bash

# Script para reiniciar Docker con opciones
echo "🐳 Ecodisseny Docker Manager"
echo ""
echo "Selecciona una opción:"
echo "1) Reinicio normal (conservar datos)"
echo "2) Reconstruir imagen (conservar datos)"
echo "3) Reset completo (borrar todos los datos)"
echo "4) Solo reset BD (conservar archivos media)"
echo "5) Logs del contenedor"
echo ""
read -p "Opción (1-5): " option

case $option in
    1)
        echo "🔄 Reiniciando sin borrar datos..."
        docker-compose down
        docker-compose up
        ;;
    2)
        echo "🔨 Reconstruyendo imagen..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up
        ;;
    3)
        echo "⚠️  BORRARÁS TODOS LOS DATOS. ¿Continuar? (y/N)"
        read -p "Confirmar: " confirm
        if [[ $confirm == [yY] ]]; then
            echo "🗑️  Reset completo..."
            docker-compose down --volumes --remove-orphans
            docker system prune -f
            docker-compose build --no-cache
            docker-compose up
        else
            echo "❌ Cancelado"
        fi
        ;;
    4)
        echo "🗑️  Borrando solo base de datos..."
        docker-compose down
        docker volume rm ecodisseny_dj_pg_postgres_data 2>/dev/null || true
        docker-compose up
        ;;
    5)
        echo "📋 Logs del contenedor web:"
        docker-compose logs -f web
        ;;
    *)
        echo "❌ Opción inválida"
        ;;
esac
