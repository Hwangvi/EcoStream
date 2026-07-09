import { useDashboard } from './hooks/useDashboard'
import { ZONAS, ZONA_LABELS } from './constants/zonas'
import DashboardLayout from './layouts/DashboardLayout'
import { ToastProvider } from './components/Toast'
import TarjetaSensor from './components/TarjetaSensor'
import ListaAlertas from './components/ListaAlertas'
import GraficoSensores from './components/GraficoSensores'
import AgenteIA from './components/AgenteIA'
import ExportadorPDF from './components/ExportadorPDF'

function App() {
  const {
    sensoresFiltrados,
    alertasFiltradas,
    zonaSeleccionada,
    setZonaSeleccionada,
    filtrarAlertasPorZona,
    setFiltrarAlertasPorZona,
    errorApi,
    dispararAnomalia,
    limpiarHistorico,
    tieneAlertaCentro,
    tieneAlertaSur,
  } = useDashboard()

  return (
    <ToastProvider>
      <DashboardLayout errorApi={errorApi}>
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
                {ZONAS.map((zona) => {
                  const activa = zonaSeleccionada === zona
                  const alerta = (zona === 'CENTRO' && tieneAlertaCentro) || (zona === 'SUR' && tieneAlertaSur)
                  return (
                    <button
                      key={zona}
                      onClick={() => setZonaSeleccionada(zona)}
                      className={`relative rounded-md px-4 py-1.5 font-mono text-xs font-medium transition-all duration-150 flex items-center gap-1.5 cursor-pointer
                        ${activa ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      {ZONA_LABELS[zona]}
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
                    onClick={dispararAnomalia}
                    className="w-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold py-2.5 rounded shadow-lg shadow-red-900/20 transition-all active:scale-95 font-mono"
                  >
                    SIMULAR ALERTA ({zonaSeleccionada})
                  </button>
                </div>

                <ExportadorPDF/>
                  
                <button 
                  onClick={limpiarHistorico}
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
      </DashboardLayout>
    </ToastProvider>
  )
}

export default App
