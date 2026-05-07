async function deleteCurso(id) {
  const res  = await fetch(`/cursos/delete/${id}`, { method: 'POST' });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.href = '/cursos', 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

async function submitCurso(e) {
  e.preventDefault();
  document.querySelectorAll('#form-curso .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/cursos/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nuevo-curso');
    showToast(json.message);
    e.target.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('c-' + (json.field || 'nombre') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}
