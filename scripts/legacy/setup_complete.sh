#!/bin/bash

# =============================================================================
# 🚀 SCRIPT MAESTRO - Reinicio completo del proyecto Ecodisseny
# =============================================================================
# Este script realiza un reinicio completo:
# 1. Borra todas las migraciones
# 2. Reinicia la base de datos (opcional)  
# 3. Crea nuevas migraciones
# 4. Carga fixtures maestros
# 5. Crea usuarios y perfiles automáticamente
# =============================================================================

echo "🚀 REINICIO COMPLETO DEL PROYECTO ECODISSENY"
echo "============================================="
echo ""
echo "Este proceso incluirá:"
echo "  📁 Borrado de migraciones"
echo "  🗃️ Reinicio de base de datos (opcional)"
echo "  ⚙️ Recreación de migraciones"
echo "  📥 Carga de fixtures maestros"
echo "  👥 Creación de usuarios y perfiles"
echo ""

read -p "¿Continuar con el reinicio completo? (s/n): " confirm
if [[ $confirm != "s" ]]; then
  echo "❌ Cancelado."
  exit 1
fi

echo ""
echo "🎯 Iniciando proceso..."

# Paso 1: Ejecutar reset de migraciones
echo "📋 Paso 1: Reiniciando migraciones y base de datos..."
./reset_migrations.sh

echo ""
echo "🎉 ¡REINICIO COMPLETO FINALIZADO!"
echo ""
echo "📊 ESTADO FINAL:"
echo "  ✅ Base de datos limpia"
echo "  ✅ Migraciones recreadas"  
echo "  ✅ Fixtures cargados"
echo "  ✅ Usuarios creados"
echo "  ✅ Perfiles configurados"
echo ""
echo "🔐 ACCESO AL SISTEMA:"
echo "  👑 Administradores: mulastone, gonzalo"
echo "  👤 Usuarios: sarah, pilar, santiago, roger"
echo "  🔑 Contraseña para todos: ecodisseny2024"
echo ""
echo "🚀 Para iniciar el servidor:"
echo "    python manage.py runserver"
