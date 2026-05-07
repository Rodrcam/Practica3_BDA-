import uuid
from flask import Blueprint, request, render_template, jsonify, abort
from models import OperacionesProfesor
from models import Profesores
from config import PAGE_SIZE

profesores_bp = Blueprint('profesores', __name__, url_prefix="/profesores")


@profesores_bp.route('/')
def home():
    q    = request.args.get('q', '').strip()
    page = max(1, request.args.get('page', 1, type=int))

    all_rows = OperacionesProfesor().get_all_teachers_with_count()

    if q:
        ql = q.lower()
        all_rows = [r for r in all_rows if ql in r[1].lower()]

    filtered    = len(all_rows)
    total       = OperacionesProfesor().get_count()
    total_pages = max(1, -(-filtered // PAGE_SIZE))
    page        = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    rows  = all_rows[start:start + PAGE_SIZE]

    p_start = max(1, page - 2)
    p_end   = min(total_pages, p_start + 4)
    pages   = list(range(p_start, p_end + 1))

    return render_template(
        "profesores/list.html",
        title="Profesores",
        rows=rows,
        total=total,
        filtered=filtered,
        q=q,
        page=page,
        total_pages=total_pages,
        pages=pages,
    )


@profesores_bp.route('/<profesor_id>')
def detail(profesor_id):
    gestor = OperacionesProfesor()
    profesor = gestor.get_by_id(profesor_id)
    if not profesor:
        abort(404)
    cursos = gestor.get_cursos_by_profesor(profesor_id)
    return render_template(
        "profesores/detail.html",
        title=profesor[1],
        profesor=profesor,
        cursos=cursos,
    )


@profesores_bp.route('/delete/<profesor_id>', methods=['POST'])
def delete(profesor_id):
    try:
        OperacionesProfesor().delete_by_id(profesor_id)
        return jsonify(ok=True, message='Profesor eliminado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@profesores_bp.route('/new', methods=['POST'])
def new():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify(ok=False, error='El nombre es obligatorio.')
    try:
        profesor = Profesores(id=str(uuid.uuid4()), nombre=nombre)
        OperacionesProfesor().insert_one_teacher(profesor=profesor)
        return jsonify(ok=True, message=f'Profesor "{nombre}" creado correctamente.')
    except Exception as e:
        return jsonify(ok=False, error=str(e))
