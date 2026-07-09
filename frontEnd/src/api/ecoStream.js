const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const fetchJSON = async (url, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${url}`, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
};

export const getDashboard = () => fetchJSON('/api/dashboard');

export const getAlertas = () => fetchJSON('/api/alertas');

export const inyectarAnomalia = (zona) => {
  const zonaObjetivo = zona === 'TODAS' ? 'CENTRO' : zona;
  return fetchJSON(`/api/alertas/inyectar-anomalia?zona=${zonaObjetivo}`, {
    method: 'POST',
  });
};

export const limpiarAlertas = () =>
  fetchJSON('/api/alertas/reset', { method: 'POST' });

export const analizarConIA = (zona) =>
  fetchJSON('/api/ia/analizar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zona }),
  });

export const exportarPDF = async () => {
  const response = await fetch(`${API_BASE_URL}/api/alertas/exportar`);
  
  const respuestaClon = response.clone();
  let datos;
  try {
    datos = await respuestaClon.json();
  } catch {
    datos = null;
  }

  if (datos && datos.status === 'error') {
    throw new Error(datos.message);
  }

  if (!response.ok) {
    throw new Error('Fallo en la descarga');
  }

  return response.blob();
};
