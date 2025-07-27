# 🧾 Revisión global App `pressupostos`

Este documento resume el análisis funcional y técnico realizado sobre la app `pressupostos`, su integración con `maestros`, formularios, JS y lógica de negocio.

---

## ✅ MODELOS (`pressupostos/models.py`)

- [x] Modelado completo, coherente con la lógica de negocio.
- [ ] Validaciones críticas también en `clean()` del modelo (`PressupostosLineas`).
- [ ] Considerar propiedades calculadas (`@property`) como `total`, `subtotal`.
- [x] Correcta relación con modelos de `maestros` y `projectes`.
- [x] Manejo de versiones PDF con `PressupostPDFVersion`.
- [ ] (Opcional) Agregar campo `motiu` o `comentari` en `PressupostPDFVersion`.
- [ ] Confirmar si se usará `managed = False` permanentemente.

---

## ✅ FORMULARIOS (`pressupostos/forms.py`)

- [x] Validación completa en `PressupostLineaForm`.
- [x] Validación de relación `client` ↔ `projecte`.
- [x] Campos `readonly` definidos por `widgets`.
- [x] Uso correcto de `inlineformset_factory`.
- [ ] Añadir `forms.DecimalField(localize=True)` si se desea mostrar 1.000,00.
- [ ] Refactor opcional: separar lógica `formset` en archivo aparte si crece.

---

## ✅ VISTAS (`pressupostos/views.py`)

- [x] CRUD completo: `form`, `list`, `delete`, `detail`, `pdf`.
- [x] Uso de `transaction.atomic()` para garantizar integridad.
- [ ] Añadir `@login_required` donde aplique.
- [x] Lógica PDF con `WeasyPrint` bien estructurada.
- [x] Endpoints AJAX funcionando correctamente (`tasques`, `hores`, `recurs`, etc.).
- [ ] Manejo de errores en AJAX: usar `JsonResponse({"error": ...}, status=400)`.

---

## ✅ JAVASCRIPT (`pressupostos.js`)

- [x] Carga dinámica de `projectes`, `tasques`, `recurso`, `increment_hores`.
- [x] Clonado correcto de líneas (`formset` JS dinámico).
- [x] Cálculos automáticos alineados con backend.
- [x] Actualización del total general.
- [ ] Modularización futura (`setupLinea()`, `calcularSubtotal()`).
- [ ] Migrar selectos AJAX simples a HTMX si se desea.
- [ ] Mostrar errores AJAX en UI (div `.alert`, etc.).

---

## ✅ PLANTILLA HTML (`form.html`)

- [x] Claridad en la distribución: tabla de cabecera + líneas.
- [x] Campos y estructura alineados con el backend.
- [x] Manejo correcto de `empty_form` para clonación.
- [x] Inclusión correcta del script con `{% block extra_scripts %}`.
- [ ] Dividir visualmente secciones con `<fieldset>` o `div.card`.
- [ ] Añadir `readonly` o alerta visual si `tancat=True`.

---

## ✅ ESTILOS (`styles.css`)

- [x] Uso de clases `col-*` para control de anchura por campo.
- [x] Estilo limpio y responsivo.
- [x] Inputs `readonly` bien diferenciados.
- [ ] (Opcional) Añadir clases `is-invalid` con errores del servidor para feedback visual.
- [ ] (Opcional) Mejoras en accesibilidad con `aria-label`.

---

## ✅ TESTS (`pressupostos/tests.py`)

- [ ] Añadir tests unitarios para:
  - Validación de formularios
  - Cálculo de líneas
  - Generación de PDF
  - Endpoints AJAX (`get_increment_hores`, etc.)

---

## 🔚 Conclusión

> App `pressupostos` bien migrada desde Flask, lógica sólida y mantenible. Recomendaciones enfocadas a seguridad, claridad visual, y robustez futura.
