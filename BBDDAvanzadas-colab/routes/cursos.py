import uuid
from flask import Blueprint, request, render_template, jsonify, abort
from models import OperacionesCurso, OperacionesProfesor
from models import Cursos
from config import PAGE_SIZE

cursos_bp = Blueprint('cursos', __name__, url_prefix="/cursos")


@cursos_bp.route('/')
def home():
    q    = request.args.get('q', '').strip()
    page = max(1, request.args.get('page', 1, type=int))

    all_rows = OperacionesCurso().get_all_courses_with_count()

    if q:
        ql = q.lower()
        all_rows = [r for r in all_rows if ql in r[1].lower() or ql in r[2].lower()]

    filtered    = len(all_rows)
    total       = OperacionesCurso().get_count()
    total_pages = max(1, -(-filtered // PAGE_SIZE))
    page        = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    rows  = all_rows[start:start + PAGE_SIZE]

    p_start = max(1, page - 2)
    p_end   = min(total_pages, p_start + 4)
    pages   = list(range(p_start, p_end + 1))

    profesores = OperacionesProfesor().get_all_teachers()

    return render_template(
        "cursos/list.html",
        title="Cursos",
        rows=rows,
        total=total,
        filtered=filtered,
        q=q,
        page=page,
        total_pages=total_pages,
        pages=pages,
        profesores=profesores,
    )


@cursos_bp.route('/<curso_id>')
def detail(curso_id):
    gestor = OperacionesCurso()
    curso  = gestor.get_by_id(curso_id)
    if not curso:
        abort(404)
    alumnos = gestor.get_alumnos_by_curso(curso_id)
    return render_template(
        "cursos/detail.html",
        title=curso[1],
        curso=curso,
        alumnos=alumnos,
    )


@cursos_bp.route('/delete/<curso_id>', methods=['POST'])
def delete(curso_id):
    try:
        OperacionesCurso().delete_by_id(curso_id)
        return jsonify(ok=True, message='Curso eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@cursos_bp.route('/new', methods=['POST'])
def new():
    nombre      = request.form.get('nombre', '').strip()
    profesor_id = request.form.get('profesor_id', '').strip()

    if not nombre:
        return jsonify(ok=False, field='nombre', error='El nombre es obligatorio.')
    if not profesor_id:
        return jsonify(ok=False, field='profesor_id', error='Selecciona un profesor.')

    try:
        curso = Cursos(id=str(uuid.uuid4()), nombre=nombre, profesor_id=profesor_id)
        OperacionesCurso().insert_one_course(curso=curso)
        return jsonify(ok=True, message=f'Curso "{nombre}" creado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
