import { useState } from 'react'
import { exportarPDF } from '../api/ecoStream'
import { useToast } from '../hooks/useToast'

function ExportadorPDF() {
  const [exportando, setExportando] = useState(false)
  const { addToast } = useToast()

  const manejarDescarga = async () => {
    setExportando(true)
    try {
      const blob = await exportarPDF()
      const enlaceDescarga = document.createElement('a')
      enlaceDescarga.href = window.URL.createObjectURL(blob)
      enlaceDescarga.download = "Reporte_EcoStream_100_Recientes.pdf"
      document.body.appendChild(enlaceDescarga)
      enlaceDescarga.click()
      enlaceDescarga.remove()
      addToast('Reporte PDF descargado correctamente', 'success')
    } catch (error) {
      console.error("Error al exportar los logs:", error)
      addToast(error.message || "No se pudo compilar el archivo PDF", 'error')
    } finally {
      setExportando(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
      <div>
        <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
          Exportación de Auditoría
        </h3>
        <p className="text-[11px] text-slate-500 font-mono mt-0.5">Descargar reporte técnico de las últimas 100 entradas</p>
      </div>

      <button
        onClick={manejarDescarga}
        disabled={exportando}
        className="rounded bg-indigo-500 px-4 py-1.5 font-mono text-xs font-bold text-slate-950 hover:bg-indigo-400 transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 whitespace-nowrap"
      >
        {exportando ? '📊 Generando...' : '📥 Descargar Reporte (100 últimos registros)'}
      </button>
    </div>
  )
}

export default ExportadorPDF
