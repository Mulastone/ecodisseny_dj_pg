# ⏱️ Guía Completa de Carga de Horas

Esta guía te enseñará todo lo que necesitas saber### **Paso 1: Formulario de Registro**

Al hacer clic en **"Nova Càrrega"**, verás un formulario con estos campos:

| Campo | Descripción | Ejemplo | Dependencia | ¿Obligatorio? |
|-------|-------------|---------|-------------|---------------|
| 👥 **Filtrar per Client** | **[FILTRO]** Cliente para filtrar opciones | Prueba, Ensisa | - | ❌ No |
| 📁 **Filtrar per Projecte** | **[FILTRO]** Proyecto para filtrar presupuestos | Proy prueba, Abarset | Depende del cliente | ❌ No |
| 📋 **Pressupost** | Proyecto/presupuesto donde trabajaste | Lista filtrada | Depende de filtros anteriores | ✅ Sí |istrar tus horas de trabajo de manera eficiente en Ecodisseny.

## 🎯 ¿Qué es la Carga de Horas?

La **Carga de Horas** es el sistema que te permite registrar el tiempo que dedicas a cada proyecto y tarea específica. Es fundamental para:

- 📊 **Seguimiento de proyectos**: Control del tiempo invertido
- 💰 **Facturación**: Base para cobros a clientes
- 📈 **Productividad**: Análisis de rendimiento personal
- 🎯 **Planificación**: Estimación de futuros proyectos

## 🚀 Acceso Rápido

### **URLs principales**:
- **Nueva carga**: `/carregahores/nova/`
- **Mis cargas**: `/carregahores/meves/`
- **Editar carga**: `/carregahores/editar/{id}/`

### **Navegación**:
1. Desde el menú principal: **⏱️ Carga de Horas**
2. Accesos rápidos disponibles según tu rol

## 📋 Registro de Nuevas Horas

### **🆕 Sistema de Filtros Dependientes**

Para facilitar la búsqueda de proyectos, ahora dispones de **filtros inteligentes y dependientes**:

| 🔍 Filtro | Función | Dependencia | Beneficio |
|-----------|---------|-------------|-----------|
| **👥 Filtrar per Client** | Filtra proyectos y presupuestos del cliente | - | Encuentra rápidamente trabajos por cliente |
| **📁 Filtrar per Projecte** | Filtra presupuestos del proyecto | Depende del cliente | Localiza trabajos específicos por proyecto |
| **📋 Pressupost** | Presupuesto final seleccionado | Depende del cliente y proyecto | Selección final precisa |

#### **🔗 Cómo Funcionan las Dependencias**

El sistema de filtros está diseñado para guiarte paso a paso:

1. **👥 Selecciona Cliente** (opcional):
   - Se filtran automáticamente los **proyectos** de ese cliente
   - Se filtran automáticamente los **presupuestos** de ese cliente
   - Los filtros se actualizan en tiempo real

2. **📁 Selecciona Proyecto** (opcional):
   - Se filtran automáticamente los **presupuestos** de ese proyecto específico
   - Solo muestra presupuestos del cliente Y proyecto seleccionados

3. **📋 Selecciona Pressupost** (obligatorio):
   - Lista final filtrada según tus selecciones anteriores
   - Solo presupuestos donde tienes permisos de trabajo

#### **💡 Casos de Uso Prácticos**

**Escenario 1: Buscar por Cliente**
```
1. Cliente: "Ensisa" → Se filtran proyectos y presupuestos de Ensisa
2. Presupuesto: Lista solo presupuestos de Ensisa
```

**Escenario 2: Buscar por Proyecto Específico**
```
1. Cliente: "Prueba" → Se filtran proyectos de Prueba
2. Proyecto: "Proy prueba" → Se filtran presupuestos de ese proyecto
3. Presupuesto: Lista solo presupuestos del proyecto específico
```

**Escenario 3: Búsqueda Directa**
```
1. Presupuesto: Selecciona directamente de la lista completa
   (Sin usar filtros - funciona como siempre)
```

#### **🔐 Permisos y Filtros**

Los filtros respetan automáticamente tus permisos:

- **👑 Administradores**: Ven todos los clientes, proyectos y presupuestos abiertos
- **👥 Recursos**: Solo ven clientes, proyectos y presupuestos donde están asignados y abiertos

**Cómo usar los filtros:**
1. **[Opcional]** Selecciona un cliente para filtrar
2. **[Opcional]** Selecciona un proyecto para filtrar (se actualiza según cliente)
3. **[Obligatorio]** Selecciona el presupuesto (filtrado según selecciones previas)
4. Continúa con el proceso normal de registro

### **Paso 1: Formulario de Registro**

Al hacer clic en **"Nova Càrrega"**, verás un formulario con estos campos:

| Campo | Descripción | Ejemplo | ¿Obligatorio? |
|-------|-------------|---------|---------------|
| � **Filtrar per Client** | **[NUEVO]** Filtro opcional por cliente | Prueba, Ensisa | ❌ No |
| 🔍 **Filtrar per Projecte** | **[NUEVO]** Filtro opcional por proyecto | Proy prueba, Abarset | ❌ No |
| 🏗️ **Pressupost** | Proyecto en el que trabajaste | Proy prueba, Abarset | ✅ Sí |
| 📋 **Linia** | Línea específica del presupuesto | Se carga automáticamente | ✅ Sí |
| ⏰ **Hores** | Tiempo trabajado en horas | 1.5, 2.25, 8 | ✅ Sí |
| 📅 **Data** | Fecha del trabajo realizado | 2025-10-05 | ✅ Sí |
| 📝 **Observacions** | Descripción del trabajo | "Dibujo de planos nivel 1" | ❌ No |

### **Paso 2: Uso de Filtros (Nuevo)**

**🎯 Escenario típico:**
1. **Tienes muchos presupuestos** y quieres encontrar uno específico
2. **Selecciona el cliente** en "Filtrar per Client" 
3. **Automáticamente** se mostrarán solo los presupuestos de ese cliente
4. **Opcionalmente** selecciona también un proyecto para afinar más
5. **Selecciona el presupuesto** de la lista filtrada

**📊 Datos disponibles actualmente:**
- 👥 **Clientes**: Prueba, Ensisa
- 📁 **Proyectos**: Proy prueba, Abarset  
- 🏗️ **Presupuestos**: Prova, prova1, y otros

### **Paso 3: Selección de Proyecto**

**Proyectos disponibles actualmente**:
- 🏗️ **Proy prueba** - Cliente: Prueba
- 🏢 **Abarset** - Cliente: Ensisa

> 💡 **Nota**: Solo verás los proyectos en los que tu recurso está autorizado a trabajar.

### **Paso 4: Líneas de Presupuesto**

Una vez seleccionado el presupuesto, las líneas se cargarán automáticamente. Cada línea representa:

- **Trabajo específico**: (ej: Aixecament Edifici, Informe, Proposta Disseny)
- **Tarea concreta**: (ej: Dibuix Plànols, Revisió, Amidament)
- **Recurso asignado**: Tu recurso debe coincidir
- **Estado**: Solo líneas abiertas (no de precio cerrado)

### **Paso 4: Registro de Horas**

**Formatos aceptados**:
- ✅ `8` = 8 horas
- ✅ `1.5` = 1 hora 30 minutos
- ✅ `2.25` = 2 horas 15 minutos
- ✅ `0.5` = 30 minutos
- ❌ `1:30` = No válido
- ❌ `1h 30m` = No válido

### **Paso 5: Observaciones**

**Ejemplos de buenas observaciones**:
- ✅ "Dibujo de planos - Planta baja"
- ✅ "Revisión de cálculos estructurales"
- ✅ "Reunión con cliente - Ajustes diseño"
- ✅ "Aixecament edifici - Fachada norte"

**Evita observaciones vagas**:
- ❌ "Trabajo vario"
- ❌ "Cosas del proyecto"
- ❌ "Tiempo en oficina"

## 📊 Gestión de tus Registros

### **Ver tus Cargas de Horas**

En **"Meves Càrregues"** podrás:

- 📋 **Listar** todos tus registros
- 🔍 **Filtrar** por fecha, proyecto, o presupuesto
- 📈 **Ordenar** por cualquier columna
- ✏️ **Editar** registros existentes
- 🗑️ **Eliminar** registros incorrectos

## 🎯 Ejemplos Prácticos con Filtros

### **Ejemplo 1: Trabajo para Cliente Específico**

**Situación**: Necesitas registrar horas trabajadas para el cliente "Prueba"

**Pasos**:
1. Ve a **Nueva Carga** (`/carregahores/nova/`)
2. En **"Filtrar per Client"** selecciona: `Prueba`
3. Verás solo presupuestos del cliente Prueba:
   - ✅ Prova
   - ✅ prova1
   - ✅ (otros presupuestos de Prueba)
4. Selecciona el presupuesto correcto
5. Continúa con el registro normal

### **Ejemplo 2: Búsqueda por Proyecto**

**Situación**: Trabajaste en el proyecto "Abarset" pero hay muchos presupuestos

**Pasos**:
1. En **"Filtrar per Projecte"** selecciona: `Abarset`
2. Automáticamente se mostrarán solo presupuestos del proyecto Abarset
3. La lista se reduce significativamente
4. Selecciona fácilmente el presupuesto correcto

### **Ejemplo 3: Filtrado Combinado**

**Situación**: Quieres ser muy específico en tu búsqueda

**Pasos**:
1. **Cliente**: Selecciona `Ensisa`
2. **Proyecto**: Selecciona `Abarset`  
3. **Resultado**: Solo presupuestos de Ensisa en proyecto Abarset
4. Lista muy reducida y específica

### **Ejemplo 4: Sin Filtros (Modo Tradicional)**

**Situación**: Prefieres ver todos los presupuestos disponibles

**Pasos**:
1. Deja ambos filtros en `--- Filtrar per... ---`
2. Verás todos los presupuestos según tus permisos
3. Funciona igual que antes de la actualización

## 💡 Consejos para Filtros

### **🚀 Buenas Prácticas**
- ✅ **Usa filtros** cuando tengas más de 5 presupuestos
- ✅ **Empieza por cliente** si trabajas con pocos clientes
- ✅ **Usa proyecto** cuando un cliente tiene múltiples proyectos
- ✅ **Combina filtros** para búsquedas muy específicas

### **⚡ Casos de Uso Típicos**
- 🎯 **Muchos presupuestos**: Usa filtros para reducir opciones
- 🏢 **Cliente recurrente**: Filtra por cliente primero
- 📁 **Proyecto grande**: Filtra por proyecto específico
- 🔍 **Búsqueda rápida**: Combina cliente + proyecto

### **Información mostrada**:

| Columna | Qué muestra | Ejemplo |
|---------|-------------|---------|
| **Data** | Fecha del trabajo | 27/09/2025 |
| **Usuari** | Tu nombre de usuario | mulastone |
| **Recurs** | Tu recurso asignado | Gonzalo (Intern) |
| **Pressupost** | Proyecto trabajado | Proy prueba |
| **Treball** | Tipo de trabajo | Aixecament Edifici |
| **Tasca** | Tarea específica | Dibuix Plànols |
| **Hores** | Tiempo registrado | 1.50 |

### **Acciones disponibles**:
- ✏️ **Editar**: Modificar cualquier campo del registro
- 🗑️ **Eliminar**: Borrar registro (con confirmación)

## 🔒 Permisos y Restricciones

### **Por Tipo de Recurso**:

#### **👤 Recursos Internos** (Gonzalo, Sarah, Pilar, Ana García)
- ✅ Acceso completo a sus registros
- ✅ Pueden trabajar en múltiples proyectos
- ✅ Edición y eliminación de registros propios
- ✅ Registro en cualquier línea de presupuesto asignada

#### **🤝 Colaboradores** (Santiago, Roger)  
- ✅ Acceso a proyectos específicos asignados
- ✅ Pueden tener restricciones por línea
- ✅ Funcionalidad básica de registro
- ⚠️ Posibles limitaciones según contrato

#### **🌐 Recursos Externos**
- ❌ Sin acceso directo al sistema
- ℹ️ Sus horas las registra un administrador

### **Validaciones Automáticas**:

El sistema verifica automáticamente:
- ✅ **Proyecto abierto**: No puedes registrar en proyectos cerrados
- ✅ **Línea válida**: La línea debe pertenecer al presupuesto
- ✅ **Recurso autorizado**: Tu recurso debe poder trabajar en esa línea
- ✅ **Presupuesto abierto**: No se puede registrar en presupuestos cerrados
- ✅ **Formato horas**: Debe ser un número decimal válido

## 💡 Consejos y Mejores Prácticas

### **⚡ Eficiencia en el Registro**

1. **Registra diariamente**: No acumules varios días
2. **Sé consistente**: Usa siempre el mismo nivel de detalle
3. **Verifica antes de guardar**: Revisa proyecto, línea y horas
4. **Usa observaciones útiles**: Describe qué hiciste específicamente

### **🎯 Precisión en los Datos**

- **Horas exactas**: Registra el tiempo real trabajado
- **Proyecto correcto**: Verifica que seleccionaste el proyecto adecuado
- **Línea apropiada**: Elige la línea que mejor describe tu trabajo
- **Fecha correcta**: Usa la fecha real del trabajo, no la de registro

### **📱 Trucos de Navegación**

- **Autocompletado**: El sistema recordará tus selecciones frecuentes
- **Validación en tiempo real**: Los errores se muestran antes de guardar
- **Navegación rápida**: Usa las URLs directas para acceso rápido

## 🚨 Problemas Comunes y Soluciones

### **❓ "No aparecen opciones en los filtros"**

**Posibles causas y soluciones**:
1. **No tienes presupuestos asignados**: Contacta al administrador
2. **Todos los presupuestos están cerrados**: No hay proyectos activos
3. **Error de carga**: Recarga la página
4. **Permisos insuficientes**: Tu recurso no está configurado

### **❓ "Los filtros no funcionan correctamente"**

**Verificaciones**:
1. ✅ **JavaScript habilitado** en tu navegador
2. ✅ **Página completamente cargada** antes de usar filtros
3. ✅ **Selecciones válidas** en los filtros
4. ✅ **Limpia filtros** si ves comportamiento extraño

### **❓ "No aparecen líneas de presupuesto"**

**Posibles causas y soluciones**:
1. **No has seleccionado presupuesto**: Primero elige el presupuesto
2. **Filtros muy restrictivos**: Ajusta o limpia los filtros
3. **Proyecto cerrado**: Contacta al administrador
4. **Sin líneas asignadas**: Tu recurso no está autorizado en ese proyecto
5. **Error de carga**: Recarga la página

### **❓ "Error al guardar el registro"**

**Verificaciones**:
1. ✅ **Todos los campos obligatorios** están completos
2. ✅ **Formato de horas** es correcto (usar punto, no coma)
3. ✅ **Fecha válida** no es futura ni muy antigua
4. ✅ **Proyecto abierto** y disponible

### **❓ "Los filtros no muestran opciones"**

**Posibles razones y soluciones**:

1. **👥 Sin clientes asignados**:
   - **Causa**: No tienes presupuestos asignados como recurso
   - **Solución**: Contacta al administrador para asignación de proyectos

2. **📁 Sin proyectos tras seleccionar cliente**:
   - **Causa**: El cliente no tiene proyectos con presupuestos donde estés asignado
   - **Solución**: Verifica que has sido asignado a líneas de presupuestos de ese cliente

3. **📋 Sin presupuestos tras filtrar**:
   - **Causa**: No hay presupuestos abiertos en esa combinación cliente/proyecto
   - **Solución**: Prueba con otros filtros o sin filtros

4. **🔄 Los filtros no se actualizan**:
   - **Causa**: Problema de JavaScript o conexión
   - **Solución**: Refresca la página (F5) o limpia la caché del navegador

**📝 Consejos para usar filtros**:
- Si no encuentras un proyecto, prueba **sin usar filtros**
- Los filtros son **opcionales** - puedes trabajar sin ellos
- **Reinicia** los filtros seleccionando la opción vacía

### **❓ "No puedo editar un registro"**

**Posibles razones**:
- 🔒 **Presupuesto cerrado**: Solo lectura
- ⏰ **Registro muy antiguo**: Puede haber restricciones temporales
- 👤 **No es tu registro**: Solo puedes editar tus propias horas
- 🔧 **Permisos insuficientes**: Contacta al administrador

### **❓ "Las líneas no corresponden al trabajo"**

**Solución**:
1. **Verifica el presupuesto**: ¿Es el proyecto correcto?
2. **Consulta al responsable**: Puede haber líneas específicas para tu trabajo
3. **Contacta administración**: Para resolver asignaciones de líneas

## 📊 Información del Sistema

### **Datos de Ejemplo Disponibles**:

**Tipos de Trabajo Configurados**:
- 🏗️ **Aixecament Edifici**: Levantamiento topográfico
- 📄 **Informe**: Documentación y reportes
- 🎨 **Proposta Disseny**: Propuestas de diseño
- 🎯 **Decoració**: Trabajos de decoración
- 📐 **Avantprojecte**: Anteproyectos

**Tareas Disponibles**:
- ✏️ **Dibuix Plànols**: Elaboración de planos
- 🔍 **Revisió**: Revisión y control de calidad
- 📊 **Informe**: Elaboración de informes
- 📏 **Amidament**: Mediciones y cálculos
- 🏗️ **Aixecament Edifici**: Levantamiento de edificios

### **🔧 Características Técnicas de los Filtros**:

**JavaScript Dinámico**:
- ⚡ **Actualizaciones en tiempo real** sin recargar la página
- 🔗 **Filtros dependientes** que se actualizan automáticamente
- 💾 **Cache inteligente** para mejorar la velocidad

**Sistema de Permisos**:
- 🔐 **Filtrado automático** según tus asignaciones
- 👑 **Vista completa para administradores**
- 👥 **Vista limitada para recursos** (solo proyectos asignados)

**Endpoints AJAX**:
- `/carrega-hores/ajax/projectes-by-client/` - Proyectos por cliente
- `/carrega-hores/ajax/pressupostos-by-filters/` - Presupuestos filtrados
- `/carrega-hores/ajax/pressupostos-data/` - Datos completos de presupuestos

### **Recursos del Sistema**:
- **Gonzalo** (Intern) - 42.60€/h
- **Sarah** (Intern) - 19.60€/h  
- **Pilar** (Intern) - 7.50€/h
- **Ana García** (Intern) - 25.50€/h
- **Santiago** (Colaborador) - Precio cerrado
- **Roger** (Colaborador) - Precio cerrado

## 📞 Soporte y Ayuda

### **🆘 ¿Necesitas Ayuda?**

- **Problemas técnicos**: Contacta al administrador del sistema
- **Dudas de asignación**: Habla con tu supervisor de proyecto
- **Errores de datos**: Solicita corrección al responsable

### **📚 Documentación Relacionada**

- 🚀 [Inicio Rápido](inicio-rapido.md) - Guía general del sistema
- 🏗️ [Gestión de Proyectos] - Para administradores
- 📊 [Reportes y Estadísticas] - Análisis de horas trabajadas

---

## 🆕 Novedades de la Versión Actual

### **Filtros Inteligentes - Octubre 2025**

**🚀 Nueva funcionalidad**: Filtrado por cliente y proyecto

**Beneficios**:
- ⚡ **Búsqueda más rápida** de presupuestos
- 🎯 **Menos opciones irrelevantes** mostradas
- 🔍 **Filtrado combinado** para máxima precisión
- 📱 **Interfaz intuitiva** y fácil de usar

**Compatibilidad**:
- ✅ **Totalmente compatible** con el flujo anterior
- ✅ **Opcional**: Puedes usarlos o no según prefieras
- ✅ **Permisos respetados**: Solo ves lo que te corresponde
- ✅ **Todas las funcionalidades** anteriores siguen igual

**Disponibilidad**:
- 👑 **Administradores**: Ven todos los clientes y proyectos
- 👥 **Recursos**: Solo ven clientes/proyectos de sus presupuestos asignados

---

## ✅ Resumen de Acciones Clave

| Acción | URL | Descripción |
|--------|-----|-------------|
| **Nueva carga** | `/carregahores/nova/` | Registrar nuevas horas |
| **Mis cargas** | `/carregahores/meves/` | Ver todos mis registros |
| **Editar** | `/carregahores/editar/{id}/` | Modificar registro específico |
| **Eliminar** | `/carregahores/eliminar/{id}/` | Borrar registro |

_💡 **Recuerda**: Un registro preciso de horas es fundamental para el éxito de los proyectos y la rentabilidad de la empresa._