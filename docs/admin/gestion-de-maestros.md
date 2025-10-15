# 🏗️ Gestió de Mestres

La gestió de dades mestres és fonamental per al correcte funcionament del sistema Ecodisseny. Aquí es configuren tots els elements base que utilitzaran els usuaris.

## ⚙️ **Administració de Mestres**

### 🔧 **Accés al Panell**

```
1. Iniciar sessió com a administrador
2. Anar al Panell d'Administració
3. Seleccionar secció "Mestres"
4. Triar tipus de dada a gestionar
```

### ➕ **Crear Nous Elements**

```
1. Seleccionar "Afegir nou"
2. Completar formulari
3. Validar informació
4. Desar canvis
```

### ✏️ **Modificar Elements Existents**

```
1. Buscar element a la llista
2. Seleccionar "Editar"
3. Realitzar modificacions
4. Confirmar canvis
```

### 🗑️ **Eliminar Elements**

```
⚠️ PRECAUCIÓ: Només eliminar elements no utilitzats
1. Verificar que no estigui en ús
2. Seleccionar element
3. Confirmar eliminació
```

## 📋 Tipus de Dades Mestres

### 🏢 **Recursos**

Gestió de recursos humans interns i externs.

#### Tipus Recursos 

- **Interns**: Personal fix d'ecodisseny amb preu per hora tancat i usuari per carregar hores
- **Col·laborador**: Personal col·laborador d'ecodisseny normalment preu tancat. Puc optar per preu per hora i carregar hores
- **Extern**: Preu tancat per treball. Empreses externes o autònoms.

#### Recursos 

- **Tipus**: Es defineix quin tipus de recurs estic donant d'alta
- **Preu Tancat**: Defineix si el recurs té preu tancat o va per hores
- **Preu Hora**: Si va per hores s'assigna el preu hora al recurs.

#### Perfils d'usuaris

Indiquem el perfil d'usuari associat a cada recurs, cada usuari que hagi de carregar hores haurà de tenir aquesta relació d'usuari - recurs


### 📍 **Ubicacions**

Configuració d'ubicacions de treball.

- **Muntanya** 
- **Pobles**
- **Nucli Urbà**

### 📝 **Tasques**

Definició de tipus de tasques del sistema.

#### exemple Tasques

- **Amidament**
- **Aixecament edifici**
- **Informe**

#### Configuració de Tasques

```
1. Anar a Admin > Mestres > Tasques
2. Definir tasca
```

## 🎯 **Millors Pràctiques**

### ✅ **Recomanacions**

- Mantenir nomenclatura consistent
- Revisar dades regularment

### ❌ **Evitar**

- Duplicar entrades
- Eliminar dades en ús
- Modificar IDs manualment
- Crear dependències circulars

_💡 **Consell**: Mantén les dades mestres organitzades i actualitzades per garantir l'eficiència del sistema._
