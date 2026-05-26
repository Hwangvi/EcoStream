function TarjetaSensor({ sensor }) {
  const { codigo_sensor, valor, unidad_medida } = sensor

  const partes = codigo_sensor.split('-')
  const zona = partes[1] || 'URBANO'
  const tipo = partes[2] || 'MÉTRICA'
  
  let colorBadge = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  if (tipo === "RUIDO") colorBadge = "bg-amber-500/10 text-amber-400 border-amber-500/20"
  if (tipo === "TRAFICO") colorBadge = "bg-blue-500/10 text-blue-400 border-blue-500/20"

  const valorFormateado = isNaN(valor) ? valor : parseFloat(valor).toFixed(1)

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