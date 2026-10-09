# MedVision AI

Plataforma de análisis de imágenes médicas con inteligencia artificial.

## Arquitectura

```
medvision-ai/
├── backend/
│   └── fastapi-api/       ← API REST (FastAPI + SQLAlchemy + PostgreSQL)
├── ai-service/            ← Servicio de IA (pendiente)
├── frontend/              ← Interfaz web (pendiente)
├── database/              ← Scripts de BD
├── bigdata/               ← Pipeline de datos (pendiente)
├── infrastructure/        ← Infraestructura (pendiente)
└── docker-compose.yml     ← PostgreSQL local
```

## Requisitos previos

- **Python** 3.11+
- **Docker Desktop** (para PostgreSQL)
- **Git**

## Inicio rápido (Windows / PowerShell)

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Landerpro05/medvision-ai.git
cd medvision-ai
```

### 2. Arrancar PostgreSQL

```powershell
docker compose up -d postgres
```

Verificar que está corriendo:

```powershell
docker ps --filter "name=medvision-postgres"
```

### 3. Configurar variables de entorno

```powershell
cd backend\fastapi-api
Copy-Item .env.example .env
```

Editar `.env` si es necesario. **Es obligatorio cambiar `JWT_SECRET` en producción.** También debes configurar los orígenes de CORS permitidos.

```env
DATABASE_URL=postgresql://medvision:medvision_dev@localhost:5432/medvision
JWT_SECRET=your-super-secret-jwt-key-change-me-in-production
APP_NAME=medvision-backend
APP_PORT=8080
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
# SQL_ECHO=False # Cambia a True en desarrollo para ver queries SQL
```

### 4. Crear entorno virtual e instalar dependencias

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5. Configurar el primer administrador (Opcional)

Para acceder a endpoints protegidos como el listado de usuarios, necesitas una cuenta de administrador. Puedes crearla con:

```powershell
python create_admin.py --username admin --email admin@example.com --password "tu_password_seguro"
```

### 6. Arrancar la API

```powershell
uvicorn app.main:app --reload --port 8080
```

La API estará disponible en:
- **API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/docs (Pulsa en "Authorize" para iniciar sesión y usar los endpoints)
- **ReDoc**: http://localhost:8080/redoc

### 7. Ejecutar las pruebas

Las pruebas usan SQLite en memoria y **no tocan la base de datos de desarrollo**.

```powershell
python -m pytest tests/ -v
```

## Endpoints

| Método | Ruta | Descripción | Autorización |
|--------|------|-------------|--------------|
| `GET` | `/api/health` | Health check | Público |
| `POST` | `/api/auth/login`| Iniciar sesión (obtener JWT) | Público |
| `POST` | `/api/users` | Registrar nuevo usuario | Público |
| `GET` | `/api/users/{id}`| Obtener usuario por ID | Propio o ADMIN |
| `GET` | `/api/users` | Listar usuarios | Solo ADMIN |
| `POST` | `/api/studies` | Crear un estudio radiológico | Requiere Token |
| `GET` | `/api/studies` | Listar estudios del usuario | Requiere Token |
| `GET` | `/api/studies/{id}`| Consultar un estudio específico | Solo si es Propio |

### Ejemplo: registrar un usuario

```powershell
$body = @{
    username = "nuevo_usuario"
    email    = "usuario@example.com"
    password = "mipassword123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/users" `
    -Method POST -Body $body -ContentType "application/json"
```

## Migraciones de base de datos

Las tablas se gestionan mediante **Flyway** (heredado del proyecto original en Spring Boot).
Para aplicar las migraciones a PostgreSQL (incluyendo la actualización de la tabla de estudios), simplemente reinicia el contenedor de la base de datos o el contenedor de la API de Spring Boot que actúa como runner temporal de migraciones, o ejecuta el script SQL `V3__update_studies_table.sql` directamente en PostgreSQL si estás en desarrollo.

*Nota: No se debe usar Alembic para modificar tablas creadas por Flyway para evitar inconsistencias.*

## Estructura del backend

```
backend/fastapi-api/
├── .env.example          ← Variables de entorno (copiar a .env)
├── requirements.txt      ← Dependencias Python
├── pyproject.toml        ← Configuración de pytest
├── alembic.ini           ← Configuración de Alembic
├── alembic/              ← Migraciones de BD
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py           ← Punto de entrada FastAPI
│   ├── config.py         ← Configuración (pydantic-settings)
│   ├── database.py       ← Conexión a PostgreSQL (SQLAlchemy)
│   ├── security.py       ← Hash de contraseñas (bcrypt)
│   └── user/
│       ├── models.py     ← Modelo User (SQLAlchemy)
│       ├── schemas.py    ← Esquemas de validación (Pydantic)
│       ├── service.py    ← Lógica de negocio
│       └── router.py     ← Endpoints de la API
└── tests/
    ├── conftest.py       ← Fixtures de test (SQLite en memoria)
    └── test_users.py     ← Tests de la API de usuarios
```
