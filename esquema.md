## 📄 Esquema de Models i Rutes - Ecodisseny

---

### 🔄 Models (texto pla)

#### `maestros`

```text
Clients
├─ id_client (PK)
├─ nom_client
├─ r_social, nrt, telefon, mail
├─ parroquia (FK → Parroquia)
└─ poblacio (FK → Poblacio)

Parroquia
└─ id_parroquia, parroquia

Poblacio
├─ id_poblacio, poblacio, codi_postal
└─ id_parroquia (FK)

DepartamentClient
└─ id_departament, nom

PersonaContactClient
├─ id_persona_contact
├─ nom_contacte, telefon, mail
└─ id_client (FK)

Treballs
└─ id_treball, descripcio

Tasca
└─ id_tasca, tasca

TasquesTreball
├─ id_tasca (FK)
└─ id_treball (FK)

Tipusrecurso
└─ id_tipus_recurso, tipus

Recurso
├─ id_recurso, name
├─ preu_tancat (bool), preu_hora
└─ id_tipus_recurso (FK)

Ubicacio
└─ id_ubicacio, ubicacio

Hores
└─ id_hora, hores

Desplacaments
├─ id_parroquia, id_ubicacio, id_tasca (FKs)
└─ increment_hores
```

#### `projectes`

```text
Projectes
├─ id_projecte (PK)
├─ nom_projecte, data_peticio
├─ id_client (FK)
├─ id_departament, id_persona_contact (FK)
├─ id_parroquia, id_ubicacio (FK)
└─ observacions, tancat (bool)
```

#### `pressupostos`

```text
Pressupostos
├─ id_pressupost (PK)
├─ nom_pressupost, data_pressupost
├─ id_client, id_projecte, id_parroquia, id_ubicacio (FKs)
├─ observacions
└─ tancat (bool)

PressupostosLineas
├─ id_pressupost_linea (PK)
├─ id_pressupost (FK)
├─ id_treball, id_tasca, id_recurso, id_hora (FKs)
├─ quantitat, preu_tancat (bool)
├─ cost_tancat, increment_hores, hores_totals
├─ cost_hores, cost_hores_totals
├─ subtotal_linea, benefici_linea, total_linea

PressupostPDFVersion
├─ pressupost (FK → Pressupostos)
├─ version (int), arxiu (PDF file)
├─ generat_per (User FK), data_generat (auto)
```

---

### 🌐 Rutes Principals

#### `/pressupostos/`

| Ruta                 | Vista                   | Descripció                  |
| -------------------- | ----------------------- | --------------------------- |
| `/`                  | `list_pressuposts`      | Llista de pressupostos      |
| `/form/`             | `form_pressupost`       | Crear pressupost            |
| `/form/<id>/`        | `form_pressupost`       | Editar pressupost           |
| `/delete/<id>/`      | `delete_pressupost`     | Eliminar pressupost         |
| `/pdf/<id>/`         | `ver_pdf_pressupost`    | PDF inline                  |
| `/<id>/generar_pdf/` | `generar_pdf_y_guardar` | Generar nova versió PDF     |
| `/detall/<id>/`      | `detail_view`           | Històric de versions de PDF |

#### AJAX endpoints

| Ruta                              | Funció JS associada               |
| --------------------------------- | --------------------------------- |
| `/get_projectes/<id_client>/`     | Canvi client → projectes          |
| `/get_tasques/<id_treball>/`      | Canvi treball → tasques           |
| `/get_recurso/<id_recurso>/`      | Canvi recurs → config. hores/preu |
| `/get_increment_hores/?params...` | Canvi parroquia+ubicació+tasca    |

---

## 📊 Diagramas del Sistema

### 🗄️ Diagrama de Relaciones de Base de Datos

```mermaid
erDiagram
    Clients ||--o{ Projectes : "té"
    Clients ||--o{ Pressupostos : "sol·licita"
    Clients ||--o{ PersonaContactClient : "té contactes"
    Parroquia ||--o{ Poblacio : "conté"
    Parroquia ||--o{ Clients : "ubicat a"
    Poblacio ||--o{ Clients : "ubicat a"
    
    Projectes ||--o{ Pressupostos : "genera"
    Projectes }o--|| DepartamentClient : "assignat a"
    Projectes }o--|| PersonaContactClient : "contacte"
    Projectes }o--|| Parroquia : "ubicació"
    Projectes }o--|| Ubicacio : "lloc"
    
    Pressupostos ||--o{ PressupostosLineas : "conté línies"
    Pressupostos ||--o{ PressupostPDFVersion : "versions PDF"
    
    PressupostosLineas }o--|| Treballs : "tipus treball"
    PressupostosLineas }o--|| Tasca : "tasca específica"
    PressupostosLineas }o--|| Recurso : "recurs utilitzat"
    PressupostosLineas }o--|| Hores : "hores aplicades"
    
    Treballs ||--o{ TasquesTreball : "té tasques"
    Tasca ||--o{ TasquesTreball : "per a treballs"
    
    Tipusrecurso ||--o{ Recurso : "classifica"
    
    Desplacaments }o--|| Parroquia : "des de"
    Desplacaments }o--|| Ubicacio : "fins a"
    Desplacaments }o--|| Tasca : "per tasca"
    
    Clients {
        int id_client PK
        string nom_client
        string r_social
        string nrt
        string telefon
        string mail
    }
    
    Projectes {
        int id_projecte PK
        string nom_projecte
        date data_peticio
        int id_client FK
        bool tancat
    }
    
    Pressupostos {
        int id_pressupost PK
        string nom_pressupost
        date data_pressupost
        int id_projecte FK
        bool tancat
    }
    
    PressupostosLineas {
        int id_pressupost_linea PK
        int id_pressupost FK
        float quantitat
        decimal subtotal_linea
        decimal benefici_linea
        decimal total_linea
    }
```

### 🔄 Flujo de Creación de Presupuesto

```mermaid
flowchart TD
    Start([📋 Iniciar Pressupost]) --> SelectClient[👤 Seleccionar Client]
    SelectClient --> LoadProjects{Té projectes?}
    
    LoadProjects -->|Sí| SelectProject[🏢 Seleccionar Projecte]
    LoadProjects -->|No| CreateProject[➕ Crear Projecte Nou]
    CreateProject --> SelectProject
    
    SelectProject --> FillBasicData[📝 Omplir Dades Bàsiques<br/>Nom, Data, Ubicació]
    FillBasicData --> AddLine[➕ Afegir Línia]
    
    AddLine --> SelectWork[🔨 Seleccionar Treball]
    SelectWork --> LoadTasks[⚙️ Carregar Tasques AJAX]
    LoadTasks --> SelectTask[✓ Seleccionar Tasca]
    
    SelectTask --> SelectResource[🛠️ Seleccionar Recurs]
    SelectResource --> LoadResourceData[💰 Carregar Preu/Hores AJAX]
    LoadResourceData --> CalcDisplacement[📍 Calcular Increment<br/>Desplaçament AJAX]
    
    CalcDisplacement --> CalcTotals[🧮 Calcular Totals<br/>Subtotal + Benefici]
    CalcTotals --> MoreLines{Més línies?}
    
    MoreLines -->|Sí| AddLine
    MoreLines -->|No| SaveBudget[(💾 Guardar Pressupost)]
    
    SaveBudget --> GeneratePDF[📄 Generar PDF]
    GeneratePDF --> VersionControl[📚 Guardar Versió PDF]
    VersionControl --> End([✅ Pressupost Completat])
    
    style Start fill:#e1f5ff
    style End fill:#e1ffe1
    style SaveBudget fill:#ffe1ff
    style GeneratePDF fill:#fff4e1
    style LoadTasks fill:#ffe1e1
    style LoadResourceData fill:#ffe1e1
    style CalcDisplacement fill:#ffe1e1
```

### 🔌 Secuencia de Interacciones AJAX

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant F as 📝 Formulario
    participant A as ⚡ AJAX Handler
    participant S as 🖥️ Servidor Django
    participant D as 🗄️ Base de Datos
    
    U->>F: Selecciona Client
    F->>A: onChange event
    A->>S: GET /get_projectes/<id_client>/
    S->>D: Query Projectes
    D-->>S: Lista de Projectes
    S-->>A: JSON response
    A->>F: Actualitzar dropdown Projectes
    
    U->>F: Selecciona Treball
    F->>A: onChange event
    A->>S: GET /get_tasques/<id_treball>/
    S->>D: Query Tasques per Treball
    D-->>S: Lista de Tasques
    S-->>A: JSON response
    A->>F: Actualitzar dropdown Tasques
    
    U->>F: Selecciona Recurs
    F->>A: onChange event
    A->>S: GET /get_recurso/<id_recurso>/
    S->>D: Query Dades Recurs
    D-->>S: Preu, Hores, Tipus
    S-->>A: JSON response
    A->>F: Omplir camps Preu i Hores
    
    U->>F: Selecciona Parroquia + Ubicació + Tasca
    F->>A: onChange events
    A->>S: GET /get_increment_hores/?params
    S->>D: Query Desplaçaments
    D-->>S: Increment Hores
    S-->>A: JSON response
    A->>F: Aplicar increment
    A->>F: Recalcular totals (JS)
    F->>U: Mostrar totals actualitzats
    
    U->>F: Guardar Pressupost
    F->>S: POST /pressupostos/form/
    S->>D: INSERT pressupost + línies
    D-->>S: Success
    S-->>F: Redirect + Message
    F->>U: Confirmació
```

### 📦 Módulos y Dependencias

```mermaid
graph LR
    subgraph "Apps Django"
        A[maestros<br/>📚 Dades Mestres]
        B[projectes<br/>🏢 Projectes]
        C[pressupostos<br/>💰 Pressupostos]
        D[carregahores<br/>⏱️ Càrrega Hores]
        E[accounts<br/>👤 Usuaris]
        F[documentacion<br/>📄 Docs]
    end
    
    subgraph "Models Maestros"
        A --> A1[Clients]
        A --> A2[Treballs]
        A --> A3[Recursos]
        A --> A4[Ubicacions]
    end
    
    B --> A1
    B --> A4
    C --> B
    C --> A1
    C --> A2
    C --> A3
    C --> A4
    D --> B
    D --> A3
    
    style A fill:#e1f5ff
    style B fill:#ffe1e1
    style C fill:#e1ffe1
    style D fill:#fff4e1
    style E fill:#ffe1ff
    style F fill:#f0f0f0
```

---
