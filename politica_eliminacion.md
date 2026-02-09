# Polítiques d'Eliminació - Ecodisseny

Aquest document descriu les polítiques d'eliminació (on_delete) configurades en els models de l'aplicació.

## 📚 Tipus de Polítiques

- **PROTECT**: Impedeix l'eliminació si hi ha registres relacionats. Mostra un missatge d'error clar.
- **CASCADE**: Elimina automàticament tots els registres relacionats.
- **SET_NULL**: Posa el camp a NULL quan s'elimina el registre relacionat.

---

## 🔧 MÒDULS MAESTROS

### **Clients**

| Campo       | Relació   | Política     | Comportament                                    |
| ----------- | --------- | ------------ | ----------------------------------------------- |
| `parroquia` | Parroquia | **SET_NULL** | Si elimines una parròquia, el camp queda a NULL |
| `poblacio`  | Poblacio  | **SET_NULL** | Si elimines una població, el camp queda a NULL  |

⚠️ **Protegit per:**

- Projectes (PROTECT)
- Pressupostos (PROTECT)

💡 **Per eliminar un Client:**

1. Elimina primer els seus Pressupostos
2. Elimina els seus Projectes
3. Ara pots eliminar el Client (els seus contactes s'eliminaran automàticament)

---

### **Parroquia**

⚠️ **Protegit per:**

- Poblacions (PROTECT)
- Desplaçaments (PROTECT)
- Projectes (PROTECT)
- Pressupostos (PROTECT)

Però clients que la referencien només quedaran amb el camp a NULL.

---

### **Poblacio**

| Campo       | Relació   | Política    | Comportament                                    |
| ----------- | --------- | ----------- | ----------------------------------------------- |
| `parroquia` | Parroquia | **PROTECT** | No pots eliminar una parròquia si té poblacions |

⚠️ **Protegit per:**

- Clients (SET_NULL) - però no bloqueja l'eliminació

---

### **TipusRecurso**

⚠️ **Protegit per:**

- Recursos (PROTECT)

---

### **Recurso**

| Campo           | Relació      | Política    | Comportament                                       |
| --------------- | ------------ | ----------- | -------------------------------------------------- |
| `tipus_recurso` | TipusRecurso | **PROTECT** | No pots eliminar un tipus de recurs si té recursos |

⚠️ **Protegit per:**

- Línies de Pressupost (PROTECT)
- Perfils d'Usuari (PROTECT)

---

### **Ubicacio**

⚠️ **Protegit per:**

- Desplaçaments (PROTECT)
- Projectes (PROTECT)
- Pressupostos (PROTECT)

---

### **Tasca**

⚠️ **Protegit per:**

- Desplaçaments (PROTECT)
- TasquesTreball (CASCADE) - però és eliminació automàtica
- Línies de Pressupost (PROTECT)

---

### **Treball**

⚠️ **Protegit per:**

- TasquesTreball (CASCADE) - però és eliminació automàtica
- Línies de Pressupost (PROTECT)

---

### **TasquesTreball** (Taula intermèdia)

| Campo     | Relació | Política    | Comportament                                                       |
| --------- | ------- | ----------- | ------------------------------------------------------------------ |
| `tasca`   | Tasca   | **CASCADE** | Si elimines una tasca, s'eliminen les seves relacions amb treballs |
| `treball` | Treball | **CASCADE** | Si elimines un treball, s'eliminen les seves relacions amb tasques |

---

### **Desplacament**

| Campo       | Relació   | Política    | Comportament                                       |
| ----------- | --------- | ----------- | -------------------------------------------------- |
| `parroquia` | Parroquia | **PROTECT** | No pots eliminar una parròquia si té desplaçaments |
| `ubicacio`  | Ubicacio  | **PROTECT** | No pots eliminar una ubicació si té desplaçaments  |
| `tasca`     | Tasca     | **PROTECT** | No pots eliminar una tasca si té desplaçaments     |

---

### **Hores**

⚠️ **Protegit per:**

- Línies de Pressupost (PROTECT)

---

### **DepartamentClient**

⚠️ **Protegit per:**

- Projectes (PROTECT)

---

### **PersonaContactClient**

| Campo    | Relació | Política    | Comportament                                              |
| -------- | ------- | ----------- | --------------------------------------------------------- |
| `client` | Clients | **CASCADE** | Si elimines un client, s'eliminen tots els seus contactes |

⚠️ **Protegit per:**

- Projectes (PROTECT)

---

### **PerfilUsuario**

| Campo     | Relació | Política    | Comportament                                       |
| --------- | ------- | ----------- | -------------------------------------------------- |
| `user`    | User    | **CASCADE** | Si elimines un usuari, s'elimina el seu perfil     |
| `recurso` | Recurso | **PROTECT** | No pots eliminar un recurs si té usuaris assignats |

---

## 📁 MÒDUL PROJECTES

### **Projecte**

Totes les relacions usen **PROTECT**:

| Campo              | Relació              | Política    | Comportament                                    |
| ------------------ | -------------------- | ----------- | ----------------------------------------------- |
| `client`           | Clients              | **PROTECT** | No pots eliminar un client si té projectes      |
| `departament`      | DepartamentClient    | **PROTECT** | No pots eliminar un departament si té projectes |
| `persona_contacte` | PersonaContactClient | **PROTECT** | No pots eliminar un contacte si té projectes    |
| `parroquia`        | Parroquia            | **PROTECT** | No pots eliminar una parròquia si té projectes  |
| `ubicacio`         | Ubicacio             | **PROTECT** | No pots eliminar una ubicació si té projectes   |

⚠️ **Protegit per:**

- Pressupostos (PROTECT)

💡 **Per eliminar un Projecte:**

1. Elimina primer tots els Pressupostos associats
2. Ara pots eliminar el Projecte

---

## 💰 MÒDUL PRESSUPOSTOS

### **Pressupost**

Totes les relacions usen **PROTECT**:

| Campo       | Relació   | Política    | Comportament                                      |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `client`    | Clients   | **PROTECT** | No pots eliminar un client si té pressupostos     |
| `projecte`  | Projecte  | **PROTECT** | No pots eliminar un projecte si té pressupostos   |
| `parroquia` | Parroquia | **PROTECT** | No pots eliminar una parròquia si té pressupostos |
| `ubicacio`  | Ubicacio  | **PROTECT** | No pots eliminar una ubicació si té pressupostos  |

✅ **Eliminació en cascada de:**

- PressupostLinia (CASCADE) - Totes les línies del pressupost
- PressupostPDFVersion (CASCADE) - Tots els registres i **arxius físics PDF**

💡 **Per eliminar un Pressupost:**

- Simplement elimina'l. Les seves línies i versions PDF (registres + arxius físics) s'eliminaran automàticament.

---

### **PressupostLinia**

| Campo        | Relació    | Política    | Comportament                                                 |
| ------------ | ---------- | ----------- | ------------------------------------------------------------ |
| `pressupost` | Pressupost | **CASCADE** | Si elimines un pressupost, s'eliminen totes les seves línies |
| `treball`    | Treball    | **PROTECT** | No pots eliminar un treball si té línies de pressupost       |
| `tasca`      | Tasca      | **PROTECT** | No pots eliminar una tasca si té línies de pressupost        |
| `recurs`     | Recurso    | **PROTECT** | No pots eliminar un recurs si té línies de pressupost        |
| `hora`       | Hores      | **PROTECT** | No pots eliminar una hora si té línies de pressupost         |

---

### **PressupostPDFVersion**

| Campo         | Relació    | Política     | Comportament                                                 |
| ------------- | ---------- | ------------ | ------------------------------------------------------------ |
| `pressupost`  | Pressupost | **CASCADE**  | Si elimines un pressupost, s'eliminen les seves versions PDF |
| `generat_per` | User       | **SET_NULL** | Si elimines un usuari, els PDFs mantenen el camp a NULL      |

🗑️ **Eliminació d'arxius físics:**

- Quan s'elimina un `PressupostPDFVersion`, també s'elimina automàticament el **fitxer PDF físic** del servidor
- Això s'aplica tant si elimines el PDF directament com si elimines el Pressupost pare (cascada)
- Els arxius es troben a: `media/pdfs_pressupostos/`

---

## 🔄 Fluxos d'Eliminació Comuns

### ❌ Eliminar un Client

**Ordre correcte:**

1. **Elimina Pressupostos del client**
   - Les línies de pressupost s'eliminen automàticament (CASCADE)
   - Les versions PDF (registres) s'eliminen automàticament (CASCADE)
   - Els arxius PDF físics s'eliminen automàticament del servidor

2. **Elimina Projectes del client**
   - Assegura't que no tinguin pressupostos associats

3. **Elimina el Client**
   - Els contactes del client s'eliminen automàticament (CASCADE)

```python
# Exemple:
# 1. Pressupost.objects.filter(client=client).delete()
# 2. Projecte.objects.filter(client=client).delete()
# 3. client.delete()  # PersonaContactClient s'eliminen automàticament
```

---

### ❌ Eliminar un Projecte

**Ordre correcte:**

1. **Elimina tots els Pressupostos del projecte**
   - Les línies de pressupost s'eliminen automàticament (CASCADE)
   - Els registres PDF i arxius físics s'eliminen automàticament

2. **Elimina el Projecte**

```python
# Exemple:
# 1. Pressupost.objects.filter(projecte=projecte).delete()
# 2. projecte.delete()
```

---

### ❌ Eliminar un Pressupost

**Simple:**

```python
# Les línies, versions PDF (registres) i arxius físics s'eliminen automàticament
pressupost.delete()
```

---

### ❌ Eliminar un Recurs

**Verificació necessària:**

Abans d'eliminar un recurs, assegura't que:

- No té línies de pressupost associades (PROTECT)
- No té usuaris assignats amb aquest recurs (PROTECT)

---

### ❌ Eliminar una Parròquia

**Verificació necessària:**

Abans d'eliminar una parròquia, assegura't que:

- No té poblacions associades (PROTECT)
- No té desplaçaments associats (PROTECT)
- No té projectes associats (PROTECT)
- No té pressupostos associats (PROTECT)

Els clients que la referencien quedaran amb el camp a NULL (SET_NULL).

---

### ❌ Eliminar una Tasca o Treball

**Verificació necessària:**

Abans d'eliminar:

- No tingui línies de pressupost (PROTECT)
- No tingui desplaçaments (només per tasques) (PROTECT)

Les relacions TasquesTreball s'eliminen automàticament (CASCADE).

---

## 🚨 Missatges d'Error

Quan intentes eliminar un element protegit, veuràs missatges clars:

### Projecte amb pressupostos:

> "No es pot eliminar el projecte '[nom]' perquè té pressupostos associats. Elimina primer els pressupostos relacionats."

### Client amb projectes/pressupostos:

> "No es pot eliminar el client '[nom]' perquè té projectes o pressupostos associats. Elimina primer els elements relacionats."

### Pressupost (si tingués proteccions):

> "No es pot eliminar el pressupost '[nom]' perquè està protegit per altres elements. Verifica les relacions abans d'eliminar."

---

## 📊 Diagrama de Dependències

```
Client
├── CASCADE → PersonaContactClient (s'eliminen automàticament)
├── PROTECT ← Projecte (cal eliminar primer)
└── PROTECT ← Pressupost (cal eliminar primer)

Projecte
├── PROTECT → Client
├── PROTECT → DepartamentClient
├── PROTECT → PersonaContactClient
├── PROTECT → Parroquia
├── PROTECT → Ubicacio
└── PROTECT ← Pressupost (cal eliminar primer)

Pressupost
├── PROTECT → Client
├── PROTECT → Projecte
├── PROTECT → Parroquia
├── PROTECT → Ubicacio
├── CASCADE → PressupostLinia (s'eliminen automàticament)
└── CASCADE → PressupostPDFVersion (s'eliminen automàticament)

PressupostLinia
├── CASCADE → Pressupost
├── PROTECT → Treball
├── PROTECT → Tasca
├── PROTECT → Recurso
└── PROTECT → Hores
```

---

## ✅ Bones Pràctiques

1. **Abans d'eliminar**, verifica sempre les dependències en el missatge d'error de Django
2. **Ordre d'eliminació**: Sempre de fill a pare (Pressupost → Projecte → Client)
3. **Dades de referència** (Parròquia, Ubicació, etc.): Millor no eliminar-les si estan en ús
4. **Backup**: Fes còpia de seguretat abans d'eliminacions massives

---

_Última actualització: 9 de febrer de 2026_
