"""
OPERACIONES CREATE:
    Consultas para la creación de tablas, índices e inserción de nuevos registros.
"""

CREATE_ALUMNOS = """
    CREATE TABLE IF NOT EXISTS alumnos (
        id UUID PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL
    );
"""

CREATE_PROFESORES = """
    CREATE TABLE IF NOT EXISTS profesores (
        id UUID PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL
    );
"""

CREATE_CURSOS = """
    CREATE TABLE IF NOT EXISTS cursos (
        id UUID PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        profesor_id UUID NOT NULL,
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );
"""

CREATE_MATRICULAS = """
    CREATE TABLE IF NOT EXISTS matriculas (
        alumno_id UUID NOT NULL,
        curso_id UUID NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        PRIMARY KEY (alumno_id, curso_id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE,
        FOREIGN KEY (curso_id)  REFERENCES cursos(id)  ON DELETE CASCADE
    );
"""

CREATE_INDEX_CURSOS_PROFESOR_ID = """
    CREATE INDEX IF NOT EXISTS idx_cursos_profesor_id ON cursos (profesor_id);
"""

CREATE_INDEX_MATRICULAS_CURSO_ID = """
    CREATE INDEX IF NOT EXISTS idx_matriculas_curso_id ON matriculas (curso_id);
"""

CREATE_INDEX_ALUMNOS_EMAIL = """
    CREATE INDEX IF NOT EXISTS idx_alumnos_email ON alumnos (email);
"""

INSERT_ALUMNOS = """
    INSERT INTO alumnos (id, nombre, email)
    VALUES (%s, %s, %s)
"""

INSERT_PROFESORES = """
    INSERT INTO profesores (id, nombre)
    VALUES (%s, %s)
"""

INSERT_CURSOS = """
    INSERT INTO cursos (id, nombre, profesor_id)
    VALUES (%s, %s, %s)
"""

INSERT_MATRICULAS = """
    INSERT INTO matriculas (alumno_id, curso_id, created_at)
    VALUES (%s, %s, %s)
"""


"""
OPERACIONES READ:
    Consultas para la lectura y consulta de registros existentes en la base de datos.
"""

SELECT_VERSION = "SELECT version();"

COUNT_PROFESORES = "SELECT COUNT(*) FROM profesores;"
COUNT_ALUMNOS    = "SELECT COUNT(*) FROM alumnos;"
COUNT_CURSOS     = "SELECT COUNT(*) FROM cursos;"
COUNT_MATRICULAS = "SELECT COUNT(*) FROM matriculas;"

SELECT_ALL_PROFESORES = """
    SELECT id, nombre FROM profesores;
"""
SELECT_ALL_ALUMNOS = """
    SELECT id, nombre, email FROM alumnos;
"""
SELECT_ALL_CURSOS = """
    SELECT c.id, c.nombre, p.nombre AS profesor FROM cursos c
    JOIN profesores p ON c.profesor_id = p.id;
"""
SELECT_ALL_MATRICULAS = """
    SELECT a.nombre AS alumno, c.nombre AS curso, m.created_at
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    JOIN cursos c ON m.curso_id = c.id
    ORDER BY m.created_at DESC;
"""

# Consultas enriquecidas para las vistas de tabla
SELECT_ALUMNOS_WITH_COUNT = """
    SELECT a.id, a.nombre, a.email, COUNT(m.curso_id) AS n_matriculas
    FROM alumnos a
    LEFT JOIN matriculas m ON a.id = m.alumno_id
    GROUP BY a.id, a.nombre, a.email
    ORDER BY a.nombre;
"""
SELECT_PROFESORES_WITH_COUNT = """
    SELECT p.id, p.nombre,
           COUNT(DISTINCT c.id)       AS n_cursos,
           COUNT(DISTINCT m.alumno_id) AS n_alumnos
    FROM profesores p
    LEFT JOIN cursos c     ON c.profesor_id = p.id
    LEFT JOIN matriculas m ON m.curso_id = c.id
    GROUP BY p.id, p.nombre
    ORDER BY p.nombre;
"""
SELECT_CURSOS_WITH_COUNT = """
    SELECT c.id, c.nombre, p.nombre AS profesor, COUNT(m.alumno_id) AS n_alumnos
    FROM cursos c
    JOIN  profesores p  ON c.profesor_id = p.id
    LEFT JOIN matriculas m ON m.curso_id = c.id
    GROUP BY c.id, c.nombre, p.nombre
    ORDER BY c.nombre;
"""
SELECT_MATRICULAS_FULL = """
    SELECT a.nombre AS alumno, c.nombre AS curso, p.nombre AS profesor, m.created_at,
           m.alumno_id, m.curso_id
    FROM matriculas m
    JOIN alumnos a    ON m.alumno_id  = a.id
    JOIN cursos c     ON m.curso_id   = c.id
    JOIN profesores p ON c.profesor_id = p.id
    ORDER BY m.created_at DESC;
"""

# Consultas de detalle por ID
SELECT_PROFESOR_BY_ID = """
    SELECT p.id, p.nombre,
           COUNT(DISTINCT c.id)        AS n_cursos,
           COUNT(DISTINCT m.alumno_id) AS n_alumnos
    FROM profesores p
    LEFT JOIN cursos c     ON c.profesor_id = p.id
    LEFT JOIN matriculas m ON m.curso_id = c.id
    WHERE p.id = %s
    GROUP BY p.id, p.nombre;
"""
SELECT_CURSOS_BY_PROFESOR = """
    SELECT c.id, c.nombre, COUNT(m.alumno_id) AS n_alumnos
    FROM cursos c
    LEFT JOIN matriculas m ON m.curso_id = c.id
    WHERE c.profesor_id = %s
    GROUP BY c.id, c.nombre
    ORDER BY c.nombre;
"""
SELECT_ALUMNO_BY_ID = """
    SELECT a.id, a.nombre, a.email,
           COUNT(m.curso_id) AS n_matriculas
    FROM alumnos a
    LEFT JOIN matriculas m ON m.alumno_id = a.id
    WHERE a.id = %s
    GROUP BY a.id, a.nombre, a.email;
"""
SELECT_CURSOS_BY_ALUMNO = """
    SELECT c.id, c.nombre, p.nombre AS profesor, m.created_at
    FROM matriculas m
    JOIN cursos c     ON m.curso_id    = c.id
    JOIN profesores p ON c.profesor_id = p.id
    WHERE m.alumno_id = %s
    ORDER BY m.created_at DESC;
"""
SELECT_CURSO_BY_ID = """
    SELECT c.id, c.nombre, p.id AS profesor_id, p.nombre AS profesor,
           COUNT(m.alumno_id) AS n_alumnos
    FROM cursos c
    JOIN profesores p  ON c.profesor_id = p.id
    LEFT JOIN matriculas m ON m.curso_id = c.id
    WHERE c.id = %s
    GROUP BY c.id, c.nombre, p.id, p.nombre;
"""
SELECT_ALUMNOS_BY_CURSO = """
    SELECT a.id, a.nombre, a.email, m.created_at
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    WHERE m.curso_id = %s
    ORDER BY m.created_at DESC;
"""
CHECK_MATRICULA_EXISTS = """
    SELECT 1 FROM matriculas WHERE alumno_id = %s AND curso_id = %s;
"""

SELECT_PROFESORES_BY_NAME = """
    SELECT id, nombre FROM profesores WHERE nombre = %s;
"""
SELECT_ALUMNOS_BY_ID = """
    SELECT id, nombre, email FROM alumnos WHERE id = %s;
"""


"""
OPERACIONES UPDATE:
    Consultas para la modificación o actualización de registros existentes.

    Operaciones disponibles: ninguna por el momento.
"""


"""
OPERACIONES DELETE:
    Consultas para la eliminación de registros existentes en la base de datos.
"""

DELETE_PROFESOR  = "DELETE FROM profesores WHERE id = %s;"
DELETE_ALUMNO    = "DELETE FROM alumnos   WHERE id = %s;"
DELETE_CURSO     = "DELETE FROM cursos    WHERE id = %s;"
DELETE_MATRICULA = "DELETE FROM matriculas WHERE alumno_id = %s AND curso_id = %s;"
