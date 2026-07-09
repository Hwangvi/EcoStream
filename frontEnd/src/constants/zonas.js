export const ZONAS = ['TODAS', 'CENTRO', 'NORTE', 'SUR'];

export const ZONA_LABELS = {
  TODAS: 'ÁREA GLOBAL',
  CENTRO: 'ZONA CENTRO',
  NORTE: 'ZONA NORTE',
  SUR: 'ZONA SUR',
};

export const TIPO_SENSOR_COLORES = {
  RUIDO: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  TRAFICO: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  default: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
};

export const getColorTipoSensor = (tipo) => {
  return TIPO_SENSOR_COLORES[tipo] || TIPO_SENSOR_COLORES.default;
};
