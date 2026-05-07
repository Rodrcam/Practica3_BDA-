async function deleteProfesor(id) {
  const res  = await fetch(`/profesores/delete/${id}`, { method: 'POST' });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.href = '/profesores', 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

async function submitProfesor(e) {
  e.preventDefault();
  const errEl = document.getElementById('p-nombre-err');
  errEl.style.display = 'none';

  const nombre = document.getElementById('p-nombre').value.trim();
  if (!nombre) {
    errEl.textContent = 'El nombre es obligatorio.';
    errEl.style.display = 'block';
    return;
  }

  const res  = await fetch('/profesores/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nuevo-profesor');
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    errEl.textContent = json.error;
    errEl.style.display = 'block';
  }
}
