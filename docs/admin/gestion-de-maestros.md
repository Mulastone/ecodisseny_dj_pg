# 🏗️ Gestión de Maestros

La gestión de datos maestros es fundamental para el correcto funcionamiento del sistema Ecodisseny. Aquí se configuran todos los elementos base que utilizarán los usuarios.

## 📋 Tipos de Datos Maestros

### 🏢 **Recursos**

Gestión de recursos humanos y materiales del sistema.

#### Recursos Humanos

- **Técnicos**: Personal que realiza trabajos técnicos
- **Administradores**: Personal administrativo
- **Gestores**: Responsables de proyectos

#### Recursos Materiales

- **Herramientas**: Equipos y herramientas necesarias
- **Vehículos**: Transporte para desplazamientos
- **Equipos**: Maquinaria especializada

### 📍 **Ubicaciones**

Configuración de ubicaciones de trabajo.

#### Tipos de Ubicaciones

- **Oficinas**: Sedes de trabajo administrativo
- **Obras**: Lugares de trabajo en campo
- **Almacenes**: Espacios de almacenamiento

#### Gestión de Ubicaciones

```
1. Acceder a Admin > Maestros > Ubicaciones
2. Crear nueva ubicación
3. Definir nombre, dirección y tipo
4. Asignar recursos disponibles
5. Configurar horarios de trabajo
```

### 📝 **Tareas**

Definición de tipos de tareas del sistema.

#### Categorías de Tareas

- **Administrativas**: Gestión y administración
- **Técnicas**: Trabajos especializados
- **Mantenimiento**: Conservación y reparación

#### Configuración de Tareas

```
1. Ir a Admin > Maestros > Tareas
2. Definir categoría de tarea
3. Establecer duración estimada
4. Asignar recursos necesarios
5. Configurar facturación
```

## ⚙️ **Administración de Maestros**

### 🔧 **Acceso al Panel**

```
1. Iniciar sesión como administrador
2. Ir a Panel de Administración
3. Seleccionar sección "Maestros"
4. Elegir tipo de dato a gestionar
```

### ➕ **Crear Nuevos Elementos**

```
1. Seleccionar "Agregar nuevo"
2. Completar formulario
3. Validar información
4. Guardar cambios
```

### ✏️ **Modificar Elementos Existentes**

```
1. Buscar elemento en la lista
2. Seleccionar "Editar"
3. Realizar modificaciones
4. Confirmar cambios
```

### 🗑️ **Eliminar Elementos**

```
⚠️ PRECAUCIÓN: Solo eliminar elementos no utilizados
1. Verificar que no esté en uso
2. Seleccionar elemento
3. Confirmar eliminación
```

## 🔄 **Sincronización y Actualizaciones**

### 📊 **Importación Masiva**

Para cargar grandes cantidades de datos:

```
1. Preparar archivo CSV con formato correcto
2. Ir a Admin > Importar datos
3. Seleccionar archivo
4. Mapear columnas
5. Ejecutar importación
```

### 📤 **Exportación de Datos**

```
1. Seleccionar tipo de datos
2. Aplicar filtros si es necesario
3. Elegir formato de exportación
4. Descargar archivo
```

## 🎯 **Mejores Prácticas**

### ✅ **Recomendaciones**

- Mantener nomenclatura consistente
- Revisar datos regularmente
- Realizar backups antes de cambios masivos
- Documentar configuraciones especiales

### ❌ **Evitar**

- Duplicar entradas
- Eliminar datos en uso
- Modificar IDs manualmente
- Crear dependencias circulares

## 🆘 **Solución de Problemas**

### 🐛 **Problemas Comunes**

**Error: "Elemento en uso"**

- Verificar referencias en proyectos activos
- Revisar asignaciones de recursos
- Consultar historial de uso

**Datos duplicados**

- Usar herramienta de detección de duplicados
- Fusionar registros similares
- Establecer reglas de validación

## 📚 **Recursos Adicionales**

- [Configuración del Sistema](/documentacion/admin/configuracion-del-sistema/)
- [Gestión de Usuarios](/documentacion/admin/gestion-de-usuarios/)
- [Seguridad](/documentacion/admin/seguridad/)

---

_💡 **Tip**: Mantén los datos maestros organizados y actualizados para garantizar la eficiencia del sistema._
