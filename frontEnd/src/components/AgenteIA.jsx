import PropTypes from 'prop-types'
import { useState } from 'react'
import { analizarConIA } from '../api/ecoStream'

function AgenteIA({ zonaActual }) {
  const [analisis, setAnalisis] = useState(null)
  const [cargando, setCargando] = useState(false)

  const manejarAnalisis = async () => {
    setCargando(true)
    setAnalisis(null)

    try {
      const data = await analizarConIA(zonaActual)
      setAnalisis({
        diagnostico: data.diagnostico,
        recomendaciones: data.recomendaciones
      })
    } catch (error) {
      console.error("Error al invocar el agente:", error)
      setAnalisis({
        diagnostico: "Error de enlace con el agente cognitivo en Python. Revisa la consola del Backend.",
        recomendaciones: []
      })
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/60 pb-4">
        <div>
          <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
            Auditoría Cognitiva (Groq Cloud)
          </h3>
          <p className="text-[11px] text-slate-500 font-mono mt-0.5">Área de análisis: {zonaActual}</p>
        </div>
        
        <button
          onClick={manejarAnalisis}
          disabled={cargando}
          className="rounded bg-sky-500 px-3 py-1.5 font-mono text-xs font-bold text-slate-950 hover:bg-sky-400 transition-all cursor-pointer disabled:opacity-50 shrink-0"
        >
          {cargando ? '🔄 Analizando...' : '🧠 Consultar EcoAI'}
        </button>
      </div>

      {cargando && (
        <div className="rounded-lg bg-slate-950/60 border border-slate-800/80 p-4 font-mono text-xs text-slate-500 animate-pulse">
          &gt; POST /api/ia/analizar HTTP/1.1
          <br />
          &gt; Extrayendo registros de PostgreSQL y consultando Llama 3...
        </div>
      )}

      {analisis && (
        <div className="rounded-lg bg-slate-950/80 border border-slate-800/80 p-5 font-mono text-xs space-y-4">
          <div>
            <span className="text-sky-400 font-bold">&gt; DIAGNÓSTICO DE LA IA:</span>
            <p className="mt-1 text-slate-300 leading-relaxed font-sans">{analisis.diagnostico}</p>
          </div>
          {analisis.recomendaciones.length > 0 && (
            <div>
              <span className="text-emerald-400 font-bold">&gt; MEDIDAS RECOMENDADAS:</span>
              <ul className="mt-2 space-y-2 font-sans text-slate-300 list-disc list-inside">
                {analisis.recomendaciones.map((rec, idx) => (
                  <li key={idx} className="leading-relaxed">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!analisis && !cargando && (
        <div className="text-center py-2 text-xs text-slate-600 font-mono">
          Haz clic en el botón para que el agente en Python audite las alertas en la nube.
        </div>
      )}
    </div>
  )
}

export default AgenteIA

AgenteIA.propTypes = {
  zonaActual: PropTypes.string.isRequired,
}
