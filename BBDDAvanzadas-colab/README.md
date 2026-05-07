# Gestor Académico — Práctica 3 BDA

Sistema web de gestión académica construido con **Flask** y **PostgreSQL**, desarrollado como práctica de Bases de Datos Avanzadas. Permite administrar profesores, alumnos, cursos y matrículas, e incluye demostraciones interactivas de transacciones y rollback ejecutadas en tiempo real contra la base de datos.

---

## 1. Versiones del entorno

| Componente   | Versión                                  |
|--------------|------------------------------------------|
| Python       | 3.14.2                                   |
| PostgreSQL   | 17.4 (x86-64, Windows, MSVC 19.43)      |
| Flask        | 3.1.3                                    |
| psycopg2     | 2.9.12                                   |
| Faker        | (última compatible con Python 3.14)      |

---

## 2. Estructura del proyecto

```
GestorClasesBBDDA/
├── app.py                  # Factoría Flask, registro de blueprints
├── run.py                  # Punto de entrada (python run.py)
├── database_menu.py        # Menú de administración de base de datos
├── requirements.txt
├── config/
│   ├── database.ini        # Parámetros de conexión y servidor
│   ├── config.py           # Lectura de configuración con ConfigParser
│   └── load.py             # Exporta PG_*, SERVER_*, PAGE_SIZE
├── models/
│   ├── entities.py         # Dataclasses: Alumnos, Profesores, Cursos, Matriculas
│   └── db/
│       ├── decorators.py   # @with_cursor / @with_transactions
│       ├── psql.py         # Clases de operaciones CRUD
│       ├── querys.py       # Todas las consultas SQL
│       └── transacciones.py# Demos de rollback contra PostgreSQL
├── routes/
│   ├── alumnos.py
│   ├── profesores.py
│   ├── cursos.py
│   ├── matriculas.py
│   └── transacciones.py
├── templates/
│   ├── base.html
│   ├── home/, alumnos/, profesores/, cursos/, matriculas/, transacciones/
└── static/
    ├── css/base.css
    └── js/  (alumnos.js, profesores.js, cursos.js, matriculas.js, transacciones.js)
```

---

## 3. Pasos para ejecutar el proyecto

### 3.1 Requisitos previos

- Python 3.10 o superior instalado y en el PATH.
- PostgreSQL 17 en ejecución local en el puerto `5432`.
- La base de datos `BBDDAvanzadasGestorAlumnos` debe existir (ver paso 3.3).

### 3.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

`requirements.txt` incluye:

```
flask
psycopg2-binary
faker
```

### 3.3 Configurar la conexión

Editar `config/database.ini` si los parámetros de la base de datos son distintos:

```ini
[postgresql]
host=localhost
database=BBDDAvanzadasGestorAlumnos
user=postgres
password=****
port=5432

[server]
server_ip=0.0.0.0
server_port=3000

[app]
page_size=10
```

### 3.4 Inicializar las tablas y poblar datos

```bash
python database_menu.py
```

Desde el menú interactivo:

| Opción | Acción                                      |
|--------|---------------------------------------------|
| 1      | Crear tablas (si no existen)                |
| 4      | Generar datos sintéticos con Faker          |

El generador de datos crea registros de prueba con nombres en español usando la localización `es_ES` de Faker.

### 3.5 Arrancar el servidor

```bash
python run.py
```

La aplicación queda disponible en: **http://127.0.0.1:3000**

---

## 4. Conteo de filas por tabla

Los siguientes conteos corresponden al estado actual de la base de datos tras la generación de datos sintéticos:

```sql
SELECT 'profesores' AS tabla, COUNT(*) FROM profesores
UNION ALL
SELECT 'alumnos',    COUNT(*) FROM alumnos
UNION ALL
SELECT 'cursos',     COUNT(*) FROM cursos
UNION ALL
SELECT 'matriculas', COUNT(*) FROM matriculas;
```

| Tabla        | Filas  |
|--------------|-------:|
| `profesores` |    107 |
| `alumnos`    |    116 |
| `cursos`     |    116 |
| `matriculas` |  5 245 |

---

## 5. Evidencia de inserciones y matrículas

### 5.1 Inserción de un profesor

```sql
INSERT INTO profesores (id, nombre)
VALUES ('17bcd023-ed56-4385-bf9c-fa417af5d002', 'Marcelino Leonardo Calvet Blanco');
```

### 5.2 Inserción de un alumno

```sql
INSERT INTO alumnos (id, nombre, email)
VALUES ('f972a1f5-6d60-4c78-a009-83db573dccc3',
        'María Pilar Carbonell-Hernandez',
        'maria-angeles82@example.org');
```

### 5.3 Inserción de un curso

```sql
INSERT INTO cursos (id, nombre, profesor_id)
VALUES ('5415447d-ea58-4138-885a-ebc7dd21ddcf',
        'Redes de Computadores',
        '17bcd023-ed56-4385-bf9c-fa417af5d002');
```

### 5.4 Registro de matrículas

```sql
INSERT INTO matriculas (alumno_id, curso_id, created_at)
VALUES ('f972a1f5-...', '5415447d-...', '2025-11-19 23:53:48+01');
```

Muestra de matrículas existentes en la base de datos:

| Alumno                          | Curso                  | Fecha                       |
|---------------------------------|------------------------|-----------------------------|
| María Pilar Carbonell-Hernandez | Redes de Computadores  | 2025-11-19 23:53:48 +01:00  |
| María Pilar Carbonell-Hernandez | Matemáticas II         | 2024-06-18 01:48:55 +02:00  |
| Salud Guijarro Company          | Cálculo Integral       | 2026-02-19 22:44:59 +01:00  |

> La clave primaria de `matriculas` es compuesta `(alumno_id, curso_id)`, garantizando que un alumno no puede matricularse dos veces en el mismo curso.

---

## 6. Evidencia de transacciones y rollback

La sección **Transacciones** de la aplicación (`GET /transacciones/`) ejecuta tres demos en tiempo real contra PostgreSQL con `autocommit = False`, mostrando el log animado paso a paso.

### 6.1 Demo 1 — Violación de clave foránea (ROLLBACK)

Se intenta insertar una matrícula referenciando un `curso_id` inventado que **no existe** en la tabla `cursos`:

```sql
BEGIN;

INSERT INTO matriculas (alumno_id, curso_id, created_at)
VALUES ('<alumno_real>', '<uuid_inexistente>', NOW());

-- PostgreSQL lanza:
-- ERROR 23503: insert or update on table "matriculas" violates
--              foreign key constraint "matriculas_curso_id_fkey"
-- DETAIL: Key (curso_id)=(<uuid_inexistente>) is not present in table "cursos".

ROLLBACK;

-- Verificación:
SELECT COUNT(*) FROM matriculas WHERE curso_id = '<uuid_inexistente>';
-- → 0 filas. La integridad referencial se conserva. ✓
```

**Conclusión:** PostgreSQL rechaza la operación y el ROLLBACK automático garantiza que no quedan datos inconsistentes.

### 6.2 Demo 2 — Violación de clave primaria compuesta (ROLLBACK)

Se intenta insertar una matrícula cuya combinación `(alumno_id, curso_id)` **ya existe**:

```sql
BEGIN;

INSERT INTO matriculas (alumno_id, curso_id, created_at)
VALUES ('<alumno_id_existente>', '<curso_id_existente>', NOW());

-- PostgreSQL lanza:
-- ERROR 23505: duplicate key value violates unique constraint "matriculas_pkey"
-- DETAIL: La clave (alumno_id, curso_id) ya existe en matriculas.

ROLLBACK;
-- → 0 filas duplicadas. PK conservada. ✓
```

**Conclusión:** La clave primaria compuesta es el mecanismo que impide matrículas duplicadas; el ROLLBACK deja la tabla en el estado anterior.

### 6.3 Demo 3 — Transacción exitosa (COMMIT)

Se ejecuta una transacción completa demostrando el aislamiento:

```sql
BEGIN;

INSERT INTO alumnos (id, nombre, email)
VALUES ('<nuevo_uuid>', 'Alumno Demo (Transacción)', 'demo.<id>@transaccion.test');

-- Dentro de la misma TX el registro ya es visible para el propio cliente:
SELECT nombre FROM alumnos WHERE id = '<nuevo_uuid>';
-- → 'Alumno Demo (Transacción)'  ✓

-- Otros clientes aún no ven el registro (aislamiento READ COMMITTED).

COMMIT;
-- → Alumno persistido correctamente. ✓

-- Limpieza automática al finalizar la demo:
DELETE FROM alumnos WHERE id = '<nuevo_uuid>';
```

**Conclusión:** El flujo `BEGIN → INSERT → COMMIT` funciona correctamente. El aislamiento `READ COMMITTED` (nivel por defecto en PostgreSQL) garantiza que otros clientes no ven cambios no confirmados.

---

## 7. Justificación de los índices

### 7.1 Índices de clave primaria (automáticos)

PostgreSQL crea automáticamente un índice B-tree único sobre cada clave primaria:

| Índice              | Tabla        | Columna(s)              | Tipo          |
|---------------------|--------------|-------------------------|---------------|
| `alumnos_pkey`      | `alumnos`    | `id`                    | B-tree único  |
| `profesores_pkey`   | `profesores` | `id`                    | B-tree único  |
| `cursos_pkey`       | `cursos`     | `id`                    | B-tree único  |
| `matriculas_pkey`   | `matriculas` | `(alumno_id, curso_id)` | B-tree único  |

Estos índices aceleran los `JOIN` entre tablas y las búsquedas por ID en las páginas de detalle.

### 7.2 Índices adicionales aplicados en el proyecto

Las tres constantes están definidas en `models/db/querys.py` y se ejecutan automáticamente en `create_tables()` de `models/db/psql.py`, usando `IF NOT EXISTS` para que la operación sea idempotente:

```sql
CREATE INDEX IF NOT EXISTS idx_cursos_profesor_id  ON cursos    (profesor_id);
CREATE INDEX IF NOT EXISTS idx_matriculas_curso_id ON matriculas (curso_id);
CREATE INDEX IF NOT EXISTS idx_alumnos_email       ON alumnos    (email);
```

Estado actual de la base de datos (verificado con `pg_indexes`):

| Índice                    | Tabla        | Columna(s)              | Tipo         |
|---------------------------|--------------|-------------------------|--------------|
| `idx_cursos_profesor_id`  | `cursos`     | `profesor_id`           | B-tree       |
| `idx_matriculas_curso_id` | `matriculas` | `curso_id`              | B-tree       |
| `idx_alumnos_email`       | `alumnos`    | `email`                 | B-tree       |

**`idx_cursos_profesor_id`**
La consulta más frecuente en la vista de detalle de un profesor recupera todos sus cursos filtrando por `cursos.profesor_id`. Sin índice, PostgreSQL realiza un *sequential scan* sobre toda la tabla. Con el índice, el coste se reduce a `O(log n)`.

```sql
-- Consulta beneficiada:
SELECT c.id, c.nombre, COUNT(m.alumno_id)
FROM cursos c
LEFT JOIN matriculas m ON m.curso_id = c.id
WHERE c.profesor_id = $1          -- ← usa idx_cursos_profesor_id
GROUP BY c.id, c.nombre;
```

**`idx_matriculas_curso_id`**
`matriculas` es la tabla más grande (5 245 filas) y se filtra frecuentemente por `curso_id` para obtener los alumnos de un curso y para los `JOIN` en las vistas enriquecidas. El índice sobre `curso_id` evita escaneos completos en cada consulta de detalle de curso.

```sql
-- Consulta beneficiada:
SELECT a.id, a.nombre, a.email, m.created_at
FROM matriculas m
JOIN alumnos a ON m.alumno_id = a.id
WHERE m.curso_id = $1;            -- ← usa idx_matriculas_curso_id
```

**`idx_alumnos_email`**
El email es el campo de unicidad de negocio para los alumnos. Este índice acelera las validaciones de duplicado al insertar un nuevo alumno y cualquier búsqueda por email.

```sql
-- Consulta beneficiada:
SELECT id FROM alumnos WHERE email = $1;   -- ← usa idx_alumnos_email
```

### 7.3 Por qué no se indexa todo

Cada índice tiene un coste de escritura: cada `INSERT`, `UPDATE` o `DELETE` debe actualizar también los índices. Para columnas como `nombre` (búsqueda de texto libre con `ILIKE`) o `created_at` (ordenación secundaria), el beneficio no justifica el coste de mantenimiento con el volumen actual de datos.

---

## 8. Endpoints de la API

| Método | Ruta                          | Descripción                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/home/`                      | Página de inicio                         |
| GET    | `/profesores`                 | Listado paginado con búsqueda            |
| GET    | `/profesores/<id>`            | Detalle del profesor y sus cursos        |
| POST   | `/profesores/new`             | Crear nuevo profesor (JSON)              |
| POST   | `/profesores/delete/<id>`     | Eliminar profesor (JSON)                 |
| GET    | `/alumnos`                    | Listado paginado con búsqueda            |
| GET    | `/alumnos/<id>`               | Detalle del alumno y sus matrículas      |
| POST   | `/alumnos/new`                | Crear nuevo alumno (JSON)                |
| POST   | `/alumnos/delete/<id>`        | Eliminar alumno (JSON)                   |
| GET    | `/cursos`                     | Listado paginado con búsqueda            |
| GET    | `/cursos/<id>`                | Detalle del curso y alumnos matriculados |
| POST   | `/cursos/new`                 | Crear nuevo curso (JSON)                 |
| POST   | `/cursos/delete/<id>`         | Eliminar curso (JSON)                    |
| GET    | `/matriculas`                 | Listado paginado con búsqueda            |
| POST   | `/matriculas/new`             | Registrar matrícula (JSON)               |
| POST   | `/matriculas/delete`          | Eliminar matrícula (JSON)                |
| GET    | `/transacciones/`             | Página de demos de transacciones         |
| POST   | `/transacciones/run/<demo_id>`| Ejecutar demo y devolver log (JSON)      |
