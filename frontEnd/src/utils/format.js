export const formatearFechaAlerta = (fechaAlerta) => {
  if (!fechaAlerta) return '--:--';
  
  try {
    const fecha = new Date(fechaAlerta);
    if (isNaN(fecha.getTime())) return '--:--';
    
    return fecha.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '--:--';
  }
};

export const formatearValor = (valor) => {
  if (isNaN(valor)) return valor;
  return parseFloat(valor).toFixed(1);
};

export const extraerTipoSensor = (codigoSensor) => {
  const partes = codigoSensor?.split('-') || [];
  return partes[2] || 'MÉTRICA';
};

export const extraerZonaSensor = (codigoSensor) => {
  const partes = codigoSensor?.split('-') || [];
  return partes[1] || 'URBANO';
};
