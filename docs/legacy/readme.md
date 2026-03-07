# 🛠️ Ecodisseny Django App

Aplicació web per a la gestió de pressupostos, projectes i clients per Ecodisseny. Desenvolupada amb Django + Bootstrap, integra funcionalitats modernes com PDF automàtics, validacions dinàmiques i formularis interactius amb AJAX + JS.

---

## 📁 Estructura de la solució

```
├── maestros/         # Dades mestres: clients, tasques, recursos, ubicacions, etc.
├── projectes/        # Projectes dels clients (lligats a pressupostos)
├── pressupostos/     # Creació i gestió de pressupostos amb línies
├── static/           # JS, CSS i assets
├── templates/        # HTML (base, form, list, detail, pdf)
```

---

## ⚙️ Característiques clau

### 🔹 Gestió de pressupostos

- Formularis dinàmics amb múltiples línies
- Càlculs automàtics (hores, cost, benefici)
- Validació de coherència entre camps (`preu_tancat`, `hores`, etc.)

### 🔹 PDF

- Generació automàtica de pressupostos en format PDF (WeasyPrint)
- Històric de versions guardat amb usuari

### 🔹 Clients i Projectes

- Relacions clares: un pressupost pertany a un projecte, que pertany a un client
- Autocomplete amb Select2 (persona contacte, població)

### 🔹 Backend Django

- Models normalitzats amb `SafeSaveModel`
- Admin amb accions personalitzades segures
- Vistes AJAX per tasques, projectes, recursos, hores extra

### 🔹 Interfície

- Disseny responsive amb Bootstrap 4
- Estil personalitzat amb `styles.css`
- JS modular (`pressupostos.js`) per gestió de línies

---

## 🚀 Instal·lació (local)

```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Accedeix a `http://localhost:8000/pressupostos/`

---

## 🧪 Tests (si s'implementen)

```bash
python manage.py test
```

---

## 🗂️ Estandardització aplicada

- Snake_case en models i fields
- Noms d’app en singular
- `SafeDeleteAdmin` amb missatges
- Rutes `/form/`, `/delete/`, `/pdf/`, `/get_*/`

---

## 👤 Desenvolupat per

**Axel Rasmussen**
_Analista i Backend Developer_
[ecodisseny_andorra@example.com](mailto:ecodisseny_andorra@example.com)

---

## 🔐 Requisits de seguretat

- Validacions en formularis i JS
- Accés autenticat per generar/eliminar
- Suport per superusuaris (rol admin)

---

## 📌 Pendents i Millores Futures

- Tests unitaris per Pressupostos i PDF
- Sistema de permisos més granular
- Històric de modificacions i logs
- Filtres a la llista de pressupostos
- Exportació a Excel

---

**Codi lliure per a desenvolupament intern d’Ecodisseny.**
