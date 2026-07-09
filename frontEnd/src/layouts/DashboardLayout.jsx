import PropTypes from 'prop-types'

function DashboardLayout({ children, errorApi }) {
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
        {children}
      </main>

      <footer className="border-t border-slate-900/60 py-5 text-center text-[10px] text-slate-600 font-mono tracking-tight">
        EcoStream Control System: Desarrollado con React, Python & PostgreSQL || HwangVi
      </footer>
    </div>
  );
}

export default DashboardLayout;

DashboardLayout.propTypes = {
  children: PropTypes.node.isRequired,
  errorApi: PropTypes.bool,
}
