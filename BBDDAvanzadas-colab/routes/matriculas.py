import uuid
import datetime
from flask import Blueprint, request, render_template, jsonify
from models import OperacionesMatricula, OperacionesAlumno, OperacionesCurso
from models import Matriculas
from config import PAGE_SIZE

matriculas_bp = Blueprint('matriculas', __name__, url_prefix="/matriculas")


@matriculas_bp.route('/')
def home():
    q    = request.args.get('q', '').strip()
    page = max(1, request.args.get('page', 1, type=int))

    all_rows = OperacionesMatricula().get_all_enrollments_full()

    if q:
        ql = q.lower()
        all_rows = [r for r in all_rows if ql in r[0].lower() or ql in r[1].lower()]

    filtered    = len(all_rows)
    total       = OperacionesMatricula().get_count()
    total_pages = max(1, -(-filtered // PAGE_SIZE))
    page        = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    rows  = all_rows[start:start + PAGE_SIZE]

    p_start = max(1, page - 2)
    p_end   = min(total_pages, p_start + 4)
    pages   = list(range(p_start, p_end + 1))

    alumnos = OperacionesAlumno().get_all_students()
    cursos  = OperacionesCurso().get_all_courses()

    return render_template(
        "matriculas/list.html",
        title="Matrículas",
        rows=rows,
        total=total,
        filtered=filtered,
        q=q,
        page=page,
        total_pages=total_pages,
        pages=pages,
        alumnos=alumnos,
        cursos=cursos,
    )


@matriculas_bp.route('/delete', methods=['POST'])
def delete():
    alumno_id = request.form.get('alumno_id', '').strip()
    curso_id  = request.form.get('curso_id', '').strip()
    if not alumno_id or not curso_id:
        return jsonify(ok=False, error='Faltan parámetros.')
    try:
        OperacionesMatricula().delete_enrollment(alumno_id, curso_id)
        return jsonify(ok=True, message='Matrícula eliminada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@matriculas_bp.route('/new', methods=['POST'])
def new():
    alumno_id = request.form.get('alumno_id', '').strip()
    curso_id  = request.form.get('curso_id', '').strip()

    if not alumno_id:
        return jsonify(ok=False, field='alumno_id', error='Selecciona un alumno.')
    if not curso_id:
        return jsonify(ok=False, field='curso_id', error='Selecciona un curso.')

    gestor = OperacionesMatricula()
    if gestor.check_exists(alumno_id, curso_id):
        return jsonify(ok=False, field='curso_id', error='El alumno ya está matriculado en ese curso (PRIMARY KEY).')

    try:
        matricula = Matriculas(
            alumno_id=alumno_id,
            curso_id=curso_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        gestor.insert_one_enrollment(matricula=matricula)
        return jsonify(ok=True, message='Matrícula registrada correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
