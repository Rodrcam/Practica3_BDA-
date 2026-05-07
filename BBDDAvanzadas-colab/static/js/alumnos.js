async function deleteAlumno(id) {
  const res  = await fetch(`/alumnos/delete/${id}`, { method: 'POST' });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.href = '/alumnos', 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

async function submitAlumno(e) {
  e.preventDefault();
  document.querySelectorAll('#form-alumno .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/alumnos/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nuevo-alumno');
    showToast(json.message);
    e.target.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('a-' + (json.field || 'nombre') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}
