function ListaAlertas({ alertas }) {
  if (!alertas || alertas.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-xs text-slate-500 font-mono">
        Sin anomalías registradas en esta área.
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/20 backdrop-blur-sm overflow-hidden">
      <div className="max-h-[340px] overflow-y-auto divide-y divide-slate-800/60 scrollbar-thin scrollbar-thumb-slate-800">
        {alertas.map((alerta) => (
          <div key={alerta.id} className="p-4 flex flex-col gap-2 hover:bg-slate-900/40 transition-colors">
            <div className="flex items-start gap-2.5">
              <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.6)]"></div>
              <div>
                <p className="text-xs text-slate-300 leading-relaxed font-normal">{alerta.descripcion || "Sin descripción"}</p>
                <div className="mt-1.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                  <span className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 text-slate-400">
                    {alerta.codigo_sensor?.split('-')?.[2] || "N/A"}
                  </span>
                  <span className="text-red-400 font-bold">Lectura: {alerta.valor ?? 0}</span>
                </div>
              </div>
            </div>
            <div className="text-[10px] font-mono text-slate-600 text-right">
              {alerta.fecha ? alerta.fecha.toString().split(' ')[1] : "--:--"}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
export default ListaAlertas