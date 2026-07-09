import PropTypes from 'prop-types'
import { formatearFechaAlerta, extraerTipoSensor } from '../utils/format'

function ListaAlertas({ alertas }) {
  if (!alertas || alertas.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-xs text-slate-500 font-mono">
        Sin anomalías registradas en esta área.
      </div>
    )
  }

  return (
    <div className="max-h-85 overflow-y-auto divide-y divide-slate-800/60 scrollbar-thin scrollbar-thumb-slate-800">
      {alertas.map((alerta) => (
        <div 
          key={alerta.id} 
          className="p-4 flex flex-col gap-2 hover:bg-slate-900/40 transition-colors animate-in fade-in slide-in-from-right-4 duration-500"
        >
          <div className="flex items-start gap-2.5">
            <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] animate-pulse"></div>
            <div>
              <p className="text-xs text-slate-200 leading-relaxed font-medium">{alerta.descripcion || "Sin descripción"}</p>
              <div className="mt-1.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                <span className="bg-red-950/30 text-red-400 px-1.5 py-0.5 rounded border border-red-900/50">
                  {extraerTipoSensor(alerta.codigo_sensor)}
                </span>
                <span className="text-red-400 font-bold">ALERTA POR VALOR CRÍTICO</span>
              </div>
            </div>
          </div>
          <div className="text-[10px] font-mono text-slate-600 text-right">
            {formatearFechaAlerta(alerta.fecha_alerta)}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ListaAlertas

ListaAlertas.propTypes = {
  alertas: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      descripcion: PropTypes.string,
      codigo_sensor: PropTypes.string,
      fecha_alerta: PropTypes.string,
    })
  ),
}
