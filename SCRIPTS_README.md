# 🚀 Scripts de Reinicio y Configuración - Ecodisseny

Este conjunto de scripts permite reiniciar completamente el proyecto Django y configurar todos los datos necesarios.

## 📋 Scripts Disponibles

### 🎯 `setup_complete.sh` - Script Maestro

**Reinicio completo del proyecto en un solo comando**

```bash
./setup_complete.sh
```

Este script ejecuta automáticamente todos los pasos necesarios:

- Borra migraciones existentes
- Reinicia la base de datos (opcional)
- Recrea migraciones
- Carga fixtures maestros
- Crea usuarios y perfiles

### 🔧 Scripts Individuales

#### `reset_migrations.sh`

Reinicia migraciones y base de datos

```bash
./reset_migrations.sh
```

#### `load_fixtures.sh`

Carga fixtures maestros y crea usuarios

```bash
./load_fixtures.sh
```

#### `generate_fixtures.sh`

Genera fixtures desde datos existentes

```bash
./generate_fixtures.sh
```

#### `create_users_profiles.py`

Crea usuarios y perfiles (se ejecuta automáticamente)

```bash
python create_users_profiles.py
```

## 👥 Usuarios Creados

| Usuario   | Tipo  | Recurso  | Contraseña     |
| --------- | ----- | -------- | -------------- |
| mulastone | ADMIN | -        | ecodisseny2024 |
| gonzalo   | ADMIN | Gonzalo  | ecodisseny2024 |
| sarah     | USER  | Sarah    | ecodisseny2024 |
| pilar     | USER  | Pilar    | ecodisseny2024 |
| santiago  | USER  | Santiago | ecodisseny2024 |
| roger     | USER  | Roger    | ecodisseny2024 |

## 🔐 Permisos

- **👑 ADMIN** (mulastone, gonzalo): Acceso completo a pressupostos y administración
- **👤 USER** (sarah, pilar, santiago, roger): Solo pueden cargar y ver sus propias horas

## 🚀 Uso Recomendado

### Para empezar desde cero:

```bash
./setup_complete.sh
```

### Para solo cargar datos después de migraciones:

```bash
./load_fixtures.sh
```

### Para generar fixtures desde datos existentes:

```bash
./generate_fixtures.sh
```

## ⚙️ Requisitos

- Entorno virtual en `./venv_postgres/`
- PostgreSQL configurado
- Archivos fixtures en `maestros/fixtures/`

## 🗃️ Base de Datos

Los scripts pueden:

- Hacer backup automático antes de resetear
- Crear base de datos nueva
- Ejecutar migraciones limpias

## 📝 Logs

Los errores se registran en `reset_errors.log`

---

**¡Listo para producción!** 🎉
