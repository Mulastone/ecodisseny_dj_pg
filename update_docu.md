# 📝 Guía para Actualizar la Documentación

Esta guía te explica paso a paso cómo editar y mantener actualizada la documentación del sistema Ecodisseny.

## 📋 Tabla de Contenidos

- [📁 Estructura de la Documentación](#-estructura-de-la-documentación)
- [✏️ Métodos de Edición](#️-métodos-de-edición)
- [🔄 Cargar Cambios en el Sistema](#-cargar-cambios-en-el-sistema)
- [📂 Crear Nueva Documentación](#-crear-nueva-documentación)
- [🎨 Formato y Estilo](#-formato-y-estilo)
- [💾 Backup y Versionado](#-backup-y-versionado)
- [🔍 Verificar Cambios](#-verificar-cambios)
- [🛠️ Comandos Útiles](#️-comandos-útiles)

## 📁 Estructura de la Documentación

### **Ubicación de los Archivos:**

```
docs/
├── README.md                    # 📚 Documentación principal
├── troubleshooting.md          # 🛠️ Solución de problemas
├── admin/                      # 🔧 Documentación de administradores
│   ├── configuracion.md        #   ⚙️ Configuración del sistema
│   ├── usuarios.md             #   👥 Gestión de usuarios
│   ├── proyectos.md            #   📊 Gestión de proyectos
│   ├── presupuestos.md         #   💰 Gestión de presupuestos
│   ├── gestion-de-maestros.md  #   🏗️ Datos maestros
│   ├── seguridad.md            #   🔐 Configuración de seguridad
│   └── mantenimiento.md        #   🔧 Mantenimiento del sistema
├── usuario/                    # 👤 Documentación de usuarios
│   └── inicio-rapido.md        #   🚀 Guía de inicio rápido
└── dev/                        # 🛠️ Documentación de desarrolladores
    └── guia-completa-vps.md    #   🚀 Deploy completo en VPS
```

### **Categorías del Sistema:**

- **`usuario/`** → Documentación de Usuario
- **`admin/`** → Documentación de Administrador
- **`dev/`** → Documentación de Desarrollador
- **Raíz `docs/`** → Documentación General

## ✏️ Métodos de Edición

### **1. Edición Directa con Editor de Texto**

```bash
# Navegar al directorio del proyecto
cd /home/mulastone/proyectos/ecodisseny_dj_pg

# Editar con nano (recomendado para principiantes)
nano docs/admin/configuracion.md

# Editar con vim (para usuarios avanzados)
vim docs/usuario/inicio-rapido.md

# Editar con VS Code (si está disponible)
code docs/dev/guia-completa-vps.md
```

### **2. Edición desde VS Code**

Si tienes el proyecto abierto en VS Code:

1. **Navegar**: Abre la carpeta `docs/` en el explorador
2. **Seleccionar**: Haz clic en el archivo que quieres editar
3. **Editar**: Modifica el contenido en formato Markdown
4. **Guardar**: Usa `Ctrl+S` para guardar los cambios

### **3. Edición desde el Admin de Django**

#### **Acceder al Panel:**

```bash
# 1. Verificar que el servidor esté corriendo
docker-compose ps

# 2. Si no está corriendo, iniciarlo
docker-compose up -d

# 3. Abrir navegador en:
http://localhost:8000/admin/

# 4. Iniciar sesión con credenciales de administrador
```

#### **Editar Documentos:**

1. Ve a **"Documentación"** → **"Documentos markdown"**
2. Busca y selecciona el documento
3. **⚠️ NO edites "Archivo markdown"** (campo de solo lectura)
4. Puedes modificar:
   - **Título**: Nombre del documento
   - **Resumen**: Descripción breve
   - **Palabras clave**: Para búsquedas
   - **Orden**: Posición en la lista
   - **Publicado**: Visible/oculto
   - **Destacado**: Aparece resaltado

## 🔄 Cargar Cambios en el Sistema

### **Después de Editar Archivos .md:**

```bash
# Método 1: Comando de gestión (recomendado)
docker-compose exec web python manage.py cargar_documentacion --update

# Método 2: Script directo
docker-compose exec web python cargar_documentacion.py

# Verificar que se cargó correctamente
echo "✅ Documentación actualizada"
```

### **Verificar la Actualización:**

```bash
# Comprobar en el navegador
curl -s http://localhost:8000/documentacion/ | grep -q "documentacion" && echo "✅ Sistema funcionando" || echo "❌ Error en el sistema"

# Ver fecha de última actualización
docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
from django.utils import timezone
doc = DocumentoMarkdown.objects.first()
print(f'Última actualización: {doc.fecha_actualizacion}')
"
```

## 📂 Crear Nueva Documentación

### **1. Crear el Archivo**

```bash
# Elegir la carpeta apropiada según el tipo:
# - docs/admin/     → Para administradores
# - docs/usuario/   → Para usuarios finales
# - docs/dev/       → Para desarrolladores
# - docs/           → Documentación general

# Ejemplo: Crear guía para administradores
touch docs/admin/nueva-funcionalidad.md

# Abrir para editar
nano docs/admin/nueva-funcionalidad.md
```

### **2. Estructura Recomendada del Documento**

````markdown
# 📊 Título del Documento

Descripción breve y clara del contenido que encontrará el usuario.

## 📋 Visión General

Explicación general de la funcionalidad o proceso.

## 🚀 Pasos a Seguir

### Paso 1: Preparación

Instrucciones del primer paso...

### Paso 2: Configuración

```bash
# Comandos de ejemplo
comando-aqui
```
````

### Paso 3: Verificación

Cómo verificar que todo funciona correctamente...

## ⚙️ Configuración Avanzada

### Opción A

Detalles de configuración avanzada...

### Opción B

Configuraciones alternativas...

## 🔍 Solución de Problemas

### Problema Común 1

**Síntoma**: Descripción del problema
**Solución**: Pasos para solucionarlo

### Problema Común 2

**Síntoma**: Otro problema típico
**Solución**: Como resolverlo

## 💡 Tips y Recomendaciones

- ✅ **Recomendación 1**: Explicación
- ✅ **Recomendación 2**: Otra sugerencia
- ⚠️ **Precaución**: Advertencia importante

## 📚 Enlaces Relacionados

- [Configuración del Sistema](/documentacion/admin/configuracion-del-sistema/)
- [Gestión de Usuarios](/documentacion/admin/gestion-de-usuarios/)
- [Documentación Principal](/documentacion/general/readme-principal/)

---

_💡 **Tip Final**: Mensaje útil para recordar al usuario._

````

### **3. Cargar el Nuevo Documento**

```bash
# El script detecta automáticamente archivos nuevos
docker-compose exec web python cargar_documentacion.py

# Verificar que se creó
docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
print('Documentos disponibles:')
for doc in DocumentoMarkdown.objects.all().order_by('categoria__nombre', 'titulo'):
    print(f'  - {doc.titulo} ({doc.categoria.nombre})')
"
````

## 🎨 Formato y Estilo

### **Elementos de Markdown Disponibles**

````markdown
# Título Principal (H1)

## Título Secundario (H2)

### Subtítulo (H3)

#### Título Menor (H4)

**Texto en negrita**
_Texto en cursiva_
`código inline`

# Listas

- Lista con viñetas
- Segundo elemento
  - Sub-elemento

1. Lista numerada
2. Segundo elemento
   1. Sub-numeración

# Enlaces

[Texto del enlace](/documentacion/categoria/documento/)
[Enlace externo](https://ejemplo.com)

# Imágenes

![Texto alternativo](ruta/imagen.png)

# Código

```bash
comando de terminal
```
````

```python
# Código Python
def funcion():
    return "ejemplo"
```

# Citas

> Esto es una cita importante
> que puede ocupar varias líneas

# Tablas

| Columna 1   | Columna 2 | Columna 3 |
| ----------- | --------- | --------- |
| Dato 1      | Dato 2    | Dato 3    |
| Información | Más info  | Final     |

# Línea horizontal

---

````

### **Iconos Recomendados por Contexto**

```markdown
# 🚀 Funcionalidades y Acciones
🚀 Inicio/Lanzamiento    🔄 Procesos/Actualizaciones
⚡ Rápido/Inmediato      🎯 Objetivos/Metas
💡 Ideas/Tips            ✅ Correcto/Completado
❌ Error/Incorrecto      ⚠️ Advertencia/Cuidado

# 🔧 Configuración y Sistema
🔧 Configuración        ⚙️ Sistema/Engranajes
🛠️ Herramientas        🔐 Seguridad/Privacidad
🏗️ Construcción        📊 Datos/Estadísticas

# 👥 Usuarios y Gestión
👤 Usuario Individual   👥 Usuarios/Grupos
🔑 Acceso/Permisos     💰 Dinero/Presupuestos
📈 Crecimiento         📉 Descenso

# 📁 Archivos y Documentos
📁 Carpetas            📄 Documentos
📝 Escritura/Edición   📚 Biblioteca/Referencias
📖 Lectura             💾 Guardar/Backup

# 🌐 Web y Conexiones
🌐 Internet/Web        🔗 Enlaces
📱 Móvil/Responsive    🖥️ Escritorio/Desktop
💻 Computadora         📺 Pantalla/Monitor

# ⏱️ Tiempo y Estados
⏱️ Tiempo/Cronómetro   📅 Calendario/Fechas
🕐 Horario            ⏰ Alarma/Recordatorio
🔄 En proceso         ⏳ Esperando
````

### **Estructura de Enlaces Internos**

```markdown
# Enlaces a documentación interna

[Texto](/documentacion/categoria/slug-del-documento/)

# Ejemplos por categoría:

[Configuración](/documentacion/admin/configuracion-del-sistema/)
[Usuarios](/documentacion/admin/gestion-de-usuarios/)
[Inicio Rápido](/documentacion/usuario/inicio-rapido/)
[Deploy VPS](/documentacion/dev/guia-completa-vps/)
[README](/documentacion/general/readme-principal/)
```

## 💾 Backup y Versionado

### **Crear Backups Antes de Editar**

```bash
# Backup de toda la documentación
cp -r docs/ docs_backup_$(date +%Y%m%d_%H%M%S)

# Backup de un archivo específico
cp docs/admin/configuracion.md docs/admin/configuracion.md.backup.$(date +%Y%m%d)

# Verificar el backup
ls -la docs_backup_* | tail -5
```

### **Control de Versiones con Git**

```bash
# Ver estado actual
git status

# Ver diferencias
git diff docs/

# Añadir cambios específicos
git add docs/admin/configuracion.md

# Añadir toda la documentación
git add docs/

# Crear commit descriptivo
git commit -m "docs: actualizar documentación de configuración de sistema

- Agregar sección de configuración avanzada
- Corregir enlaces rotos
- Mejorar formato de códigos de ejemplo"

# Subir cambios
git push origin docker

# Ver historial de cambios
git log --oneline docs/
```

## 🔍 Verificar Cambios

### **Comprobar que se Cargó Correctamente**

```bash
# 1. Verificar contenedores activos
docker-compose ps

# 2. Cargar documentación actualizada
docker-compose exec web python manage.py cargar_documentacion --update

# 3. Verificar en base de datos
docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
from django.utils import timezone
print('📚 Documentos en el sistema:')
for doc in DocumentoMarkdown.objects.all().order_by('-fecha_actualizacion'):
    tiempo_transcurrido = timezone.now() - doc.fecha_actualizacion
    if tiempo_transcurrido.seconds < 300:  # Últimos 5 minutos
        print(f'  🆕 {doc.titulo} - Actualizado hace {tiempo_transcurrido.seconds}s')
    else:
        print(f'     {doc.titulo} - {doc.fecha_actualizacion.strftime(\"%d/%m/%Y %H:%M\")}')
"

# 4. Probar acceso web
curl -s -o /dev/null -w "Estado HTTP: %{http_code}\n" http://localhost:8000/documentacion/
```

### **Verificar Formato Markdown**

```bash
# Verificar que no hay errores de sintaxis
docker-compose exec web python -c "
import markdown
with open('docs/admin/configuracion.md', 'r') as f:
    contenido = f.read()
try:
    html = markdown.markdown(contenido)
    print('✅ Formato Markdown correcto')
except Exception as e:
    print(f'❌ Error en formato: {e}')
"
```

### **Ver Logs en Caso de Error**

```bash
# Logs del contenedor web
docker-compose logs --tail=50 web

# Logs específicos del comando de carga
docker-compose exec web python manage.py cargar_documentacion --update 2>&1 | tee carga_docs.log

# Ver errores recientes
docker-compose logs web | grep -i error | tail -10
```

## 🛠️ Comandos Útiles

### **Comandos de Edición Rápida**

```bash
# Editar documentos más comunes
alias edit-config="nano docs/admin/configuracion.md"
alias edit-users="nano docs/admin/usuarios.md"
alias edit-readme="nano docs/README.md"
alias edit-quick="nano docs/usuario/inicio-rapido.md"

# Recargar documentación
alias reload-docs="docker-compose exec web python manage.py cargar_documentacion --update"

# Verificar sistema
alias check-docs="curl -s http://localhost:8000/documentacion/ | grep -q 'Documentación' && echo '✅ OK' || echo '❌ Error'"
```

### **Flujo de Trabajo Completo**

```bash
# 1. Hacer backup
cp docs/admin/configuracion.md docs/admin/configuracion.md.backup

# 2. Editar archivo
nano docs/admin/configuracion.md

# 3. Cargar cambios
docker-compose exec web python manage.py cargar_documentacion --update

# 4. Verificar
curl -s http://localhost:8000/documentacion/admin/configuracion-del-sistema/ | grep -q "configuracion" && echo "✅ Actualizado" || echo "❌ Error"

# 5. Commit a git (opcional)
git add docs/admin/configuracion.md
git commit -m "docs: actualizar configuración del sistema"
git push origin docker
```

### **Comandos de Diagnóstico**

```bash
# Ver todos los documentos y sus URLs
docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
print('📋 Lista completa de documentación:')
for doc in DocumentoMarkdown.objects.all().order_by('categoria__nombre', 'orden', 'titulo'):
    print(f'  📄 {doc.titulo}')
    print(f'     🔗 /documentacion/{doc.categoria.slug}/{doc.slug}/')
    print(f'     📁 {doc.archivo_markdown}')
    print()
"

# Verificar archivos huérfanos (en docs/ pero no en BD)
find docs/ -name "*.md" -type f | while read archivo; do
    if ! docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
import sys
existe = DocumentoMarkdown.objects.filter(archivo_markdown='$archivo').exists()
sys.exit(0 if existe else 1)
" 2>/dev/null; then
        echo "🔍 Archivo no en BD: $archivo"
    fi
done

# Verificar enlaces rotos en documentos
docker-compose exec web python manage.py shell -c "
from documentacion.models import DocumentoMarkdown
import re
import os

print('🔍 Verificando enlaces internos...')
for doc in DocumentoMarkdown.objects.all():
    try:
        with open(doc.archivo_markdown, 'r') as f:
            contenido = f.read()

        # Buscar enlaces internos
        enlaces = re.findall(r'\[.*?\]\((/documentacion/.*?)\)', contenido)
        for enlace in enlaces:
            print(f'   📄 {doc.titulo}: {enlace}')
    except FileNotFoundError:
        print(f'❌ Archivo no encontrado: {doc.archivo_markdown}')
"
```

## 🎯 Resumen de Flujo de Trabajo

### **Para Ediciones Simples:**

```bash
1. nano docs/admin/configuracion.md
2. docker-compose exec web python manage.py cargar_documentacion --update
3. Verificar en http://localhost:8000/documentacion/
```

### **Para Cambios Importantes:**

```bash
1. cp docs/admin/archivo.md docs/admin/archivo.md.backup
2. nano docs/admin/archivo.md
3. docker-compose exec web python manage.py cargar_documentacion --update
4. git add docs/ && git commit -m "docs: descripción del cambio"
5. git push origin docker
```

### **Para Nuevos Documentos:**

```bash
1. touch docs/categoria/nuevo-documento.md
2. nano docs/categoria/nuevo-documento.md
3. docker-compose exec web python cargar_documentacion.py
4. Verificar en admin y web
```

---

## 📚 Referencias Útiles

- **Markdown Guide**: [https://www.markdownguide.org/](https://www.markdownguide.org/)
- **Iconos Emoji**: [https://emojipedia.org/](https://emojipedia.org/)
- **Admin Django**: `http://localhost:8000/admin/documentacion/documentomarkdown/`
- **Documentación Web**: `http://localhost:8000/documentacion/`

---

_💡 **Tip**: Guarda este documento como referencia rápida. Siempre haz backup antes de cambios importantes y verifica que todo funcione correctamente después de actualizar._
