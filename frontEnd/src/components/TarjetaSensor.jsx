import PropTypes from 'prop-types'
import { getColorTipoSensor } from '../constants/zonas'
import { formatearValor, extraerTipoSensor, extraerZonaSensor } from '../utils/format'

function TarjetaSensor({ sensor }) {
  const { codigo_sensor, valor, unidad_medida } = sensor

  const zona = extraerZonaSensor(codigo_sensor)
  const tipo = extraerTipoSensor(codigo_sensor)
  const colorBadge = getColorTipoSensor(tipo)
  const valorFormateado = formatearValor(valor)

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-sm transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/60">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold tracking-wider text-slate-400 font-mono">
          Zona {zona}
        </span>
        <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold tracking-tight uppercase font-mono ${colorBadge}`}>
          {tipo}
        </span>
      </div>
      
      <div className="mt-6">
        <div className="flex items-baseline gap-1.5">
          <span className="text-3xl font-light tracking-tight text-white font-mono">
            {valorFormateado}
          </span>
          <span className="text-xs font-medium text-slate-500 font-mono">
            {unidad_medida || ''}
          </span>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-800/50 flex items-center justify-between text-[11px] text-slate-500">
        <span className="font-mono text-[10px] text-slate-600">{codigo_sensor}</span>
        <div className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          <span>Live</span>
        </div>
      </div>
    </div>
  )
}

export default TarjetaSensor

TarjetaSensor.propTypes = {
  sensor: PropTypes.shape({
    codigo_sensor: PropTypes.string.isRequired,
    valor: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    unidad_medida: PropTypes.string,
  }).isRequired,
}
