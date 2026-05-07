import uuid
import re
from flask import Blueprint, request, render_template, jsonify, abort
from models import OperacionesAlumno
from models import Alumnos
from config import PAGE_SIZE

alumnos_bp = Blueprint('students', __name__, url_prefix="/alumnos")

_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


@alumnos_bp.route('/')
def home():
    q    = request.args.get('q', '').strip()
    page = max(1, request.args.get('page', 1, type=int))

    all_rows = OperacionesAlumno().get_all_students_with_count()

    if q:
        ql = q.lower()
        all_rows = [r for r in all_rows if ql in r[1].lower() or ql in r[2].lower()]

    filtered    = len(all_rows)
    total       = OperacionesAlumno().get_count()
    total_pages = max(1, -(-filtered // PAGE_SIZE))
    page        = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    rows  = all_rows[start:start + PAGE_SIZE]

    p_start = max(1, page - 2)
    p_end   = min(total_pages, p_start + 4)
    pages   = list(range(p_start, p_end + 1))

    return render_template(
        "alumnos/list.html",
        title="Alumnos",
        rows=rows,
        total=total,
        filtered=filtered,
        q=q,
        page=page,
        total_pages=total_pages,
        pages=pages,
    )


@alumnos_bp.route('/<alumno_id>')
def detail(alumno_id):
    gestor = OperacionesAlumno()
    alumno = gestor.get_by_id(alumno_id)
    if not alumno:
        abort(404)
    cursos = gestor.get_cursos_by_alumno(alumno_id)
    profesores_distintos = len({c[2] for c in cursos})
    return render_template(
        "alumnos/detail.html",
        title=alumno[1],
        alumno=alumno,
        cursos=cursos,
        profesores_distintos=profesores_distintos,
    )


@alumnos_bp.route('/delete/<alumno_id>', methods=['POST'])
def delete(alumno_id):
    try:
        OperacionesAlumno().delete_by_id(alumno_id)
        return jsonify(ok=True, message='Alumno eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@alumnos_bp.route('/new', methods=['POST'])
def new():
    nombre = request.form.get('nombre', '').strip()
    email  = request.form.get('email', '').strip()

    if not nombre:
        return jsonify(ok=False, field='nombre', error='El nombre es obligatorio.')
    if not email:
        return jsonify(ok=False, field='email', error='El email es obligatorio.')
    if not _EMAIL_RE.match(email):
        return jsonify(ok=False, field='email', error='Formato de email no válido.')

    try:
        alumno = Alumnos(id=str(uuid.uuid4()), nombre=nombre, email=email)
        OperacionesAlumno().insert_one_student(alumno=alumno)
        return jsonify(ok=True, message=f'Alumno "{nombre}" creado correctamente.')
    except Exception as e:
        err = str(e)
        if 'email' in err.lower() or 'unique' in err.lower():
            return jsonify(ok=False, field='email', error='Este email ya está registrado.')
        return jsonify(ok=False, error=err)
