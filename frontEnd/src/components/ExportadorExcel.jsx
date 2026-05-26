import { useState } from 'react'

function ExportadorExcel() {
  const [rango, setRango] = useState('dia')
  const [exportando, setExportando] = useState(false)

  const manejarDescarga = async () => {
    setExportando(true)
    try {
      const url = `http://127.0.0.1:8000/api/alertas/exportar?rango=${rango}`
      
      const respuesta = await fetch(url)
      if (!respuesta.ok) throw new Error("Fallo en la descarga")
      
      const blob = await respuesta.blob()
      const enlaceDescarga = document.createElement('a')
      enlaceDescarga.href = window.URL.createObjectURL(blob)
      enlaceDescarga.download = `EcoStream_Reporte_${rango}.csv`
      document.body.appendChild(enlaceDescarga)
      enlaceDescarga.click()
      enlaceDescarga.remove()
    } catch (error) {
      console.error("Error al exportar los logs:", error)
      alert("No se pudo compilar el archivo Excel en este momento.")
    } finally {
      setExportando(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
      <div>
        <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
          Exportación de Datos Críticos
        </h3>
        <p className="text-[11px] text-slate-500 font-mono mt-0.5">Compilación de auditorías territoriales</p>
      </div>

      <div className="flex gap-2">
        <select
          value={rango}
          onChange={(e) => setRango(e.target.value)}
          className="flex-1 rounded border border-slate-800 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-300 focus:outline-none cursor-pointer"
        >
          <option value="dia">Últimas 24 Horas</option>
          <option value="semana">Últimos 7 Días</option>
          <option value="mes">Últimos 30 Días</option>
        </select>

        <button
          onClick={manejarDescarga}
          disabled={exportando}
          className="rounded bg-emerald-500 px-4 py-1.5 font-mono text-xs font-bold text-slate-950 hover:bg-emerald-400 transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 whitespace-nowrap"
        >
          {exportando ? '📊 Generando...' : '📥 Descargar .CSV'}
        </button>
      </div>
    </div>
  )
}

export default ExportadorExcel