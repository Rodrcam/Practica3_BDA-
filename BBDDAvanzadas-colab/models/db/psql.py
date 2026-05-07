from .decorators import with_cursor, with_transactions
from .querys import (
    SELECT_VERSION, SELECT_ALL_PROFESORES, SELECT_ALL_ALUMNOS,
    SELECT_ALL_CURSOS, SELECT_ALL_MATRICULAS,
    SELECT_ALUMNOS_WITH_COUNT, SELECT_PROFESORES_WITH_COUNT,
    SELECT_CURSOS_WITH_COUNT, SELECT_MATRICULAS_FULL,
    SELECT_PROFESOR_BY_ID, SELECT_CURSOS_BY_PROFESOR,
    SELECT_ALUMNO_BY_ID, SELECT_CURSOS_BY_ALUMNO,
    SELECT_CURSO_BY_ID, SELECT_ALUMNOS_BY_CURSO,
    CHECK_MATRICULA_EXISTS,
    DELETE_PROFESOR, DELETE_ALUMNO, DELETE_CURSO, DELETE_MATRICULA,
    COUNT_PROFESORES, COUNT_ALUMNOS, COUNT_CURSOS, COUNT_MATRICULAS,
    CREATE_ALUMNOS, CREATE_CURSOS, CREATE_MATRICULAS, CREATE_PROFESORES,
    CREATE_INDEX_CURSOS_PROFESOR_ID, CREATE_INDEX_MATRICULAS_CURSO_ID, CREATE_INDEX_ALUMNOS_EMAIL,
    INSERT_ALUMNOS, INSERT_PROFESORES, INSERT_CURSOS, INSERT_MATRICULAS
)
from ..entities import Alumnos, Profesores, Cursos, Matriculas
from psycopg2 import Error
# Funciones auxiliares
def validate_email(email: str) -> bool:
    import re
    REGEX_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" 
    if re.match(REGEX_PATTERN, email):
        return True   
    return False

# Operaciones principales de PostgreSQL
class PostgreSQL():
    # Obtener la version de PostgreSQL
    @with_cursor
    def obtain_database_version(self, cursor):
        cursor.execute(SELECT_VERSION)
        return cursor.fetchone()

    # Creacion de todas las tablas de Postgresql
    @with_transactions
    def create_tables(self, cursor):
        cursor.execute(CREATE_ALUMNOS)
        cursor.execute(CREATE_PROFESORES)
        cursor.execute(CREATE_CURSOS)
        cursor.execute(CREATE_MATRICULAS)
        cursor.execute(CREATE_INDEX_CURSOS_PROFESOR_ID)
        cursor.execute(CREATE_INDEX_MATRICULAS_CURSO_ID)
        cursor.execute(CREATE_INDEX_ALUMNOS_EMAIL)

# Operaciones del profesor
class OperacionesProfesor():
    # Operaciones de lectura   
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_PROFESORES)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    @with_cursor
    def get_all_teachers(self, cursor):
        try:
            cursor.execute(SELECT_ALL_PROFESORES)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los profesores:", e)
            return []

    @with_cursor
    def get_all_teachers_with_count(self, cursor):
        try:
            cursor.execute(SELECT_PROFESORES_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los profesores:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, profesor_id: str):
        try:
            cursor.execute(SELECT_PROFESOR_BY_ID, (profesor_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el profesor:", e)
            return None

    @with_cursor
    def get_cursos_by_profesor(self, cursor, profesor_id: str):
        try:
            cursor.execute(SELECT_CURSOS_BY_PROFESOR, (profesor_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos del profesor:", e)
            return []

    
    # Operaciones de escritura
    @with_transactions
    def insert_one_teacher(self, cursor, profesor:Profesores):
        params = (profesor.id, profesor.nombre)
        cursor.execute(INSERT_PROFESORES, params)
        print(f"Se ha ingresado el profesor: {profesor} dentro de la base de datos")

    @with_transactions
    def delete_by_id(self, cursor, profesor_id: str):
        cursor.execute(DELETE_PROFESOR, (profesor_id,))

# Operaciones del Alumno
class OperacionesAlumno():   
    # Operaciones de lectura   
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_ALUMNOS)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    @with_cursor
    def get_all_students(self, cursor):
        try:
            cursor.execute(SELECT_ALL_ALUMNOS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los estudiantes:", e)
            return []

    @with_cursor
    def get_all_students_with_count(self, cursor):
        try:
            cursor.execute(SELECT_ALUMNOS_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los estudiantes:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, alumno_id: str):
        try:
            cursor.execute(SELECT_ALUMNO_BY_ID, (alumno_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el alumno:", e)
            return None

    @with_cursor
    def get_cursos_by_alumno(self, cursor, alumno_id: str):
        try:
            cursor.execute(SELECT_CURSOS_BY_ALUMNO, (alumno_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos del alumno:", e)
            return []


    # Operaciones de escritura
    @with_transactions
    def insert_one_student(self, cursor, alumno:Alumnos):
        # Verificamos el formato del correo
        if not alumno.email or not validate_email(alumno.email):
            raise Exception("Hay un error procesando el correo electrónico.")

        params = (alumno.id, alumno.nombre, alumno.email)
        cursor.execute(INSERT_ALUMNOS, params)
        print(f"Se ha ingresado el alumno: {alumno} dentro de la base de datos")

    @with_transactions
    def delete_by_id(self, cursor, alumno_id: str):
        cursor.execute(DELETE_ALUMNO, (alumno_id,))

# Operaciones del Curso
class OperacionesCurso():
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_CURSOS)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_cursor
    def get_all_courses(self, cursor):
        try:
            cursor.execute(SELECT_ALL_CURSOS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos:", e)
            return []

    @with_cursor
    def get_all_courses_with_count(self, cursor):
        try:
            cursor.execute(SELECT_CURSOS_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, curso_id: str):
        try:
            cursor.execute(SELECT_CURSO_BY_ID, (curso_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el curso:", e)
            return None

    @with_cursor
    def get_alumnos_by_curso(self, cursor, curso_id: str):
        try:
            cursor.execute(SELECT_ALUMNOS_BY_CURSO, (curso_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los alumnos del curso:", e)
            return []

    @with_transactions
    def insert_one_course(self, cursor, curso: Cursos):
        params = (curso.id, curso.nombre, curso.profesor_id)
        cursor.execute(INSERT_CURSOS, params)
        print(f"Se ha ingresado el curso: {curso} dentro de la base de datos")

    @with_transactions
    def delete_by_id(self, cursor, curso_id: str):
        cursor.execute(DELETE_CURSO, (curso_id,))

# Operaciones de la matricula
class OperacionesMatricula():
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_MATRICULAS)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_cursor
    def get_all_enrollments(self, cursor):
        try:
            cursor.execute(SELECT_ALL_MATRICULAS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener las matrículas:", e)
            return []

    @with_cursor
    def get_all_enrollments_full(self, cursor):
        try:
            cursor.execute(SELECT_MATRICULAS_FULL)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener las matrículas:", e)
            return []

    @with_cursor
    def check_exists(self, cursor, alumno_id: str, curso_id: str) -> bool:
        try:
            cursor.execute(CHECK_MATRICULA_EXISTS, (alumno_id, curso_id))
            return cursor.fetchone() is not None
        except (Exception, Error) as e:
            print("Error al verificar matrícula:", e)
            return False

    @with_transactions
    def insert_one_enrollment(self, cursor, matricula: Matriculas):
        params = (matricula.alumno_id, matricula.curso_id, matricula.created_at)
        cursor.execute(INSERT_MATRICULAS, params)

    @with_transactions
    def delete_enrollment(self, cursor, alumno_id: str, curso_id: str):
        cursor.execute(DELETE_MATRICULA, (alumno_id, curso_id))


