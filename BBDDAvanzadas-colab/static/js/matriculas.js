function renderList(items, listId, hiddenId, queryId, labelFn, valueFn) {
  const list = document.getElementById(listId);
  list.innerHTML = '';
  if (!items.length) { list.style.display = 'none'; return; }
  items.slice(0, 8).forEach(item => {
    const div = document.createElement('div');
    div.className = 'autocomplete-item';
    div.innerHTML = labelFn(item);
    div.onclick = () => {
      document.getElementById(hiddenId).value = valueFn(item);
      document.getElementById(queryId).value  = item[1];
      list.style.display = 'none';
    };
    list.appendChild(div);
  });
  list.style.display = 'block';
}

function filterAlumnos(q) {
  const ql = q.toLowerCase();
  document.getElementById('m-alumno-id').value = '';
  const matches = ALUMNOS_DATA.filter(a => a[1].toLowerCase().includes(ql) || a[2].toLowerCase().includes(ql));
  renderList(
    matches, 'm-alumno-list', 'm-alumno-id', 'm-alumno-q',
    a => `${a[1]} <span>#${a[0].slice(0,8)}…</span>`,
    a => a[0]
  );
}

function filterCursos(q) {
  const ql = q.toLowerCase();
  document.getElementById('m-curso-id').value = '';
  const matches = CURSOS_DATA.filter(c => c[1].toLowerCase().includes(ql));
  renderList(
    matches, 'm-curso-list', 'm-curso-id', 'm-curso-q',
    c => c[1],
    c => c[0]
  );
}

document.addEventListener('click', e => {
  if (!e.target.closest('#m-alumno-q') && !e.target.closest('#m-alumno-list'))
    document.getElementById('m-alumno-list').style.display = 'none';
  if (!e.target.closest('#m-curso-q') && !e.target.closest('#m-curso-list'))
    document.getElementById('m-curso-list').style.display = 'none';
});

async function deleteMatricula(alumnoId, cursoId) {
  const fd = new FormData();
  fd.append('alumno_id', alumnoId);
  fd.append('curso_id',  cursoId);
  const res  = await fetch('/matriculas/delete', { method: 'POST', body: fd });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

let _pendingDeleteAlumnoId = null;
let _pendingDeleteCursoId  = null;

function confirmDeleteMatricula(alumnoId, cursoId, alumnoNombre, cursoNombre) {
  _pendingDeleteAlumnoId = alumnoId;
  _pendingDeleteCursoId  = cursoId;
  document.getElementById('confirm-delete-msg').textContent =
    `¿Eliminar la matrícula de "${alumnoNombre}" en "${cursoNombre}"?`;
  openModal('modal-confirmar-eliminar');
}

function executeDeleteMatricula() {
  deleteMatricula(_pendingDeleteAlumnoId, _pendingDeleteCursoId);
}

async function submitMatricula(e) {
  e.preventDefault();
  document.querySelectorAll('#form-matricula .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/matriculas/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nueva-matricula');
    showToast(json.message);
    e.target.reset();
    document.getElementById('m-alumno-q').value = '';
    document.getElementById('m-curso-q').value  = '';
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('m-' + (json.field || 'alumno_id') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}
