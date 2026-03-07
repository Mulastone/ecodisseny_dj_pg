# Configuración de Formatters para Django Templates

## Problema

Los formatters automáticos (como Prettier) dividen los tags de Django en múltiples líneas, rompiendo la sintaxis:

```django
❌ INCORRECTO (formateado automáticamente):
Registrades{% if filter_form.is_bound %} (amb filtres aplicats){%
endif %}

✅ CORRECTO:
Registrades{% if filter_form.is_bound %} (amb filtres aplicats){% endif %}
```

Esto causa errores 500 en producción: `Invalid block tag: 'endblock', expected 'elif', 'else' or 'endif'`

## Soluciones Implementadas

### 1. Configuración de VS Code (`.vscode/settings.json`)

- ✅ Deshabilitado `formatOnSave` para archivos HTML
- ✅ Asociación de templates con `django-html`
- ✅ Prettier configurado para respetar `.prettierignore`

### 2. EditorConfig (`.editorconfig`)

- ✅ Deshabilitado `max_line_length` para archivos HTML
- ✅ Configuración específica por tipo de archivo

### 3. Prettier Ignore (`.prettierignore`)

- ✅ Exclusión de carpeta `templates/`
- ✅ Exclusión de archivos específicos como `*_stats.html`

### 4. Prettier Config (`.prettierrc.json`)

- ✅ `printWidth: 999999` para templates HTML
- ✅ Override específico para archivos en carpeta `templates/`

## Cómo Usar

### Opción 1: Deshabilitar Formateo Automático (Recomendado)

En VS Code, para archivos HTML de Django:

1. Abre el archivo `.html`
2. Presiona `Shift+Ctrl+P` (o `Cmd+P` en Mac)
3. Escribe: `Format Document`
4. Selecciona: `Configure Default Formatter...`
5. Elige: `None - Disable Format On Save`

### Opción 2: Formatear Manualmente con Cuidado

Si necesitas formatear un template:

1. **NO uses** `Format Document` (Shift+Alt+F)
2. Formatea solo secciones pequeñas que no contengan tags Django
3. Revisa siempre que los tags `{% %}` estén en una sola línea

### Opción 3: Extensión Django para VS Code

Instala la extensión recomendada:

- **Django** (batisteo.vscode-django)
  - Syntax highlighting específico para Django
  - Mejor manejo de templates
  - Snippets útiles

## Verificación Rápida

Después de editar templates, verifica:

```bash
# Dentro del contenedor Docker
docker compose --env-file .env.dev exec web python manage.py check

# O prueba la vista específica
docker compose --env-file .env.dev exec web python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecodisseny.settings')
django.setup()
from django.template.loader import get_template
get_template('carregahores/admin_stats.html')
print('✓ Template OK')
"
```

## Configuración Manual Adicional

Si sigues teniendo problemas, añade a tu configuración personal de VS Code (`Ctrl+,`):

```json
{
  "[html]": {
    "editor.formatOnSave": false
  },
  "files.associations": {
    "**/templates/**/*.html": "django-html"
  }
}
```

## Archivos Críticos

Estos archivos **nunca** deben formatearse automáticamente:

- `templates/carregahores/admin_stats.html`
- `templates/base.html`
- Cualquier archivo con tags Django `{% %}`

## Qué Hacer si se Rompe un Template

1. Busca líneas con tags divididos:

   ```bash
   grep -n "{% if.*{%" templates/**/*.html
   grep -n "endif.*%}" templates/**/*.html
   ```

2. Une los tags en una sola línea:

   ```django
   {%
   endif %}  →  {% endif %}
   ```

3. Reinicia el contenedor:
   ```bash
   docker compose --env-file .env.dev restart web
   ```

## Prevención

- ✅ Usa las configuraciones incluidas en este proyecto
- ✅ Instala la extensión Django para VS Code
- ✅ Verifica `.prettierignore` antes de formatear
- ❌ No uses "Format Document" en templates Django
- ❌ No uses Beautify u otros formatters genéricos

---

**Nota**: Estas configuraciones ya están aplicadas en el proyecto. Solo asegúrate de que VS Code las cargue correctamente al abrir el workspace.
