import { useState, useEffect } from 'react'
import TarjetaSensor from './components/TarjetaSensor'
import ListaAlertas from './components/ListaAlertas'
import GraficoSensores from './components/GraficoSensores'
import AgenteIA from './components/AgenteIA'
import ExportadorPDF from './components/ExportadorPDF'

function App() {
  const [sensores, setSensores] = useState([])
  const [alertas, setAlertas] = useState([])
  const [zonaSeleccionada, setZonaSeleccionada] = useState('TODAS')
  const [filtrarAlertasPorZona, setFiltrarAlertasPorZona] = useState(false)
  const [errorApi, setErrorApi] = useState(false)

  const dispararAnomalia = async (zona) => {
    const zonaObjetivo = zona === 'TODAS' ? 'CENTRO' : zona
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/alertas/inyectar-anomalia?zona=${zonaObjetivo}`, {
        method: 'POST'
      });
      console.log(`Anomalía inyectada en zona: ${zonaObjetivo}`);
    } catch (err) {
      console.error("Error al inyectar anomalía:", err);
    }
  };
  const limpiarAlertas = async () => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/alertas/reset`, { method: 'POST' });
      setAlertas([]);
    } catch (err) {
      console.error("Error al limpiar:", err);
    }
  };

  useEffect(() => {
    const consultarBackend = async () => {
      try {
        const [resDashboard, resAlertas] = await Promise.all([
          fetch(`${import.meta.env.VITE_API_URL}/api/dashboard`),
          fetch(`${import.meta.env.VITE_API_URL}/api/alertas`)
        ])

        if (!resDashboard.ok || !resAlertas.ok) throw new Error('Error de conexión')

        const datosDashboard = await resDashboard.json()
        const datosAlertas = await resAlertas.json()

        setSensores(datosDashboard)
        setAlertas(datosAlertas)
        setErrorApi(false)
      } catch (err) {
        console.error("Error en sincronización:", err)
        setErrorApi(true)
      }
    }

    consultarBackend()
    const intervalo = setInterval(consultarBackend, 2000)
    return () => clearInterval(intervalo)
  }, [])

  const sensoresFiltrados = sensores.filter(sensor => {
    if (zonaSeleccionada === 'TODAS') return true
    return sensor.codigo_sensor.includes(`-${zonaSeleccionada}-`)
  })

  const alertasFiltradas = alertas.filter(alerta => {
    if (!filtrarAlertasPorZona || zonaSeleccionada === 'TODAS') return true
    return alerta.codigo_sensor.includes(`-${zonaSeleccionada}-`)
  })
  
  const tieneAlertaCentro = alertas.some(a => a.codigo_sensor.includes("CENTRO"))
  const tieneAlertaSur = alertas.some(a => a.codigo_sensor.includes("SUR"))

  return (
    <div className="flex min-h-screen flex-col bg-[#0b0f19] text-slate-200 antialiased font-sans">
      <header className="border-b border-slate-800/80 bg-[#0b0f19]/70 backdrop-blur-md py-4 px-6 sm:px-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="EcoStream Logo" className="h-20 w-auto brightness-200"/>
            <h1 className="text-base font-medium tracking-tight text-white font-mono">
              ECOSTREAM <span className="text-slate-500 font-light text-xs ml-1">/ ANALYTICS ENGINE</span>
            </h1>
          </div>
          <div className="flex items-center gap-2 rounded border border-slate-800 bg-slate-900/20 px-2.5 py-0.5 font-mono text-[10px] text-slate-400">
            <span className={`h-1 w-1 rounded-full ${errorApi ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'}`}></span>
            {errorApi ? 'NETWORK ERROR' : 'FEED SYNCHRONIZED'}
          </div>
        </div>
      </header>

      <main className="flex-1 p-6 sm:p-10 max-w-7xl mx-auto w-full space-y-8">
        {errorApi ? (
          <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-5 text-center text-xs text-red-400 font-mono">
            Error de enlace: Reconectando con la API de control urbano...
          </div>
        ) : (
          <div className="space-y-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/60 pb-5">
              <div>
                <h2 className="text-base font-normal text-white tracking-tight">Consola de Mando Territorial</h2>
                <p className="text-xs text-slate-500 font-mono mt-0.5">Segmentación operativa por cuadrantes urbanos</p>
              </div>
              
              <div className="flex rounded-lg bg-slate-900/60 p-1 border border-slate-800/80 self-start sm:self-auto">
                {['TODAS', 'CENTRO', 'NORTE', 'SUR'].map((zona) => {
                  const activa = zonaSeleccionada === zona
                  const alerta = (zona === 'CENTRO' && tieneAlertaCentro) || (zona === 'SUR' && tieneAlertaSur)
                  return (
                    <button
                      key={zona}
                      onClick={() => setZonaSeleccionada(zona)}
                      className={`relative rounded-md px-4 py-1.5 font-mono text-xs font-medium transition-all duration-150 flex items-center gap-1.5 cursor-pointer
                        ${activa ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      {zona === 'TODAS' ? 'ÁREA GLOBAL' : `ZONA ${zona}`}
                      {alerta && <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse"></span>}
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
              <div className="lg:col-span-2 space-y-8">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {sensoresFiltrados.map((sensor, index) => (
                    <TarjetaSensor key={sensor.codigo_sensor || index} sensor={sensor} />
                  ))}
                </div>
                <GraficoSensores datos={sensoresFiltrados} />
                <AgenteIA zonaActual={zonaSeleccionada} />
              </div>

              <div className="lg:col-span-1 space-y-4">
                <div className="bg-red-950/10 border border-red-900/30 p-4 rounded-xl">
                  <h3 className="text-[10px] font-bold text-red-500/70 uppercase tracking-widest mb-3">Centro de Inyección</h3>
                  <button 
                    onClick={() => dispararAnomalia(zonaSeleccionada)}
                    className="w-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold py-2.5 rounded shadow-lg shadow-red-900/20 transition-all active:scale-95 font-mono"
                  >
                    SIMULAR ALERTA ({zonaSeleccionada})
                  </button>
                </div>

                <ExportadorPDF/>
                  
                <button 
                  onClick={limpiarAlertas}
                  className="w-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-500 text-[10px] font-mono py-2 rounded transition-all"
                >
                  LIMPIAR HISTÓRICO
                </button>
                <div className="flex items-center justify-between">
                    <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">Incidentes Recientes</h3>
                    {zonaSeleccionada !== 'TODAS' && (
                      <select
                        value={filtrarAlertasPorZona ? 'ZONA' : 'TODAS'}
                        onChange={(e) => setFiltrarAlertasPorZona(e.target.value === 'ZONA')}
                        className="rounded border border-slate-800 bg-slate-950 px-2 py-0.5 font-mono text-[10px] text-slate-400 focus:outline-none cursor-pointer"
                      >
                        <option value="TODAS">Ver Todas</option>
                        <option value="ZONA">Solo Zona {zonaSeleccionada}</option>
                      </select>
                    )}
                </div>
                <ListaAlertas alertas={alertasFiltradas} />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-900/60 py-5 text-center text-[10px] text-slate-600 font-mono tracking-tight">
        EcoStream Control System: Desarrollado con React, Python & PostgreSQL || HwangVi
      </footer>
    </div>
  )
}

export default App

