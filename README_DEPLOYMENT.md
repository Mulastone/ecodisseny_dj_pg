# 🚀 Ecodisseny -- Deployment & Branching Strategy

## 📌 Overview

Este proyecto utiliza una estrategia de ramas simple y profesional junto
con Docker para separar correctamente:

-   Desarrollo (local)
-   Integración
-   Producción (VPS)

------------------------------------------------------------------------

# 🌳 Estrategia de Ramas

``` mermaid
flowchart LR

    A[feature/*<br>Desarrollo de nuevas funcionalidades]
    B[develop<br>Integración y pruebas en Docker local]
    C[main<br>Producción estable en VPS]
    D[(VPS Producción<br>docker compose --env-file .env.prod up -d --build)]

    A -->|git merge| B
    B -->|Test OK en local| C
    C -->|git push origin main| D

    subgraph Local
        A
        B
        C
    end

    subgraph Servidor
        D
    end
```

------------------------------------------------------------------------

## 🔁 Flujo de Trabajo

### 1️⃣ Crear nueva funcionalidad

``` bash
git checkout -b feature/nueva-funcionalidad
```

### 2️⃣ Integrar en develop

``` bash
git checkout develop
git merge feature/nueva-funcionalidad
```

### 3️⃣ Probar en Docker local

``` bash
docker compose --env-file .env.dev up --build
```

### 4️⃣ Pasar a producción

``` bash
git checkout main
git merge develop
git push origin main
```

En el VPS:

``` bash
git pull origin main
docker compose --env-file .env.prod up -d --build
```

------------------------------------------------------------------------

# 🐳 Arquitectura Docker

``` mermaid
flowchart LR

    Browser --> Nginx
    Nginx --> Django
    Django --> Postgres
    Django --> StaticVolume
    Django --> MediaVolume

    subgraph Docker Compose
        Django[Web Container]
        Postgres[DB Container]
        StaticVolume[(static_volume)]
        MediaVolume[(media_volume)]
    end
```

------------------------------------------------------------------------

# ⚙️ Entornos

## 🧪 Desarrollo (.env.dev)

-   DEBUG=True
-   ENVIRONMENT=dev
-   Base de datos local Docker
-   runserver

## 🚀 Producción (.env.prod)

-   DEBUG=False
-   ENVIRONMENT=prod
-   Gunicorn
-   Volúmenes persistentes
-   Base de datos PostgreSQL persistente

------------------------------------------------------------------------

# 🔐 Seguridad

-   `main` protegida en GitHub
-   Pull Request obligatorio
-   No push directo a producción
-   Variables sensibles fuera del repositorio

------------------------------------------------------------------------

# 📦 Comandos útiles

### Levantar entorno desarrollo

``` bash
docker compose --env-file .env.dev up --build
```

### Parar contenedores

``` bash
docker compose down
```

### Parar y eliminar volúmenes (⚠️ BORRA DATOS)

``` bash
docker compose down -v
```

------------------------------------------------------------------------

# 🧠 Filosofía

-   develop = entorno seguro de pruebas
-   main = solo código estable
-   Docker único archivo
-   Configuración diferenciada vía .env

------------------------------------------------------------------------

© Ecodisseny -- Arquitectura mantenible y profesional
