import PropTypes from 'prop-types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function GraficoSensores({ datos }) {
  const dataGrafico = datos.map(s => ({
    name: s.codigo_sensor.replace("SEN-", ""),
    Valor: isNaN(s.valor) ? 0 : parseFloat(s.valor),
    unidad: s.unidad_medida || ''
  }))

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-sm">
      <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono mb-4">
        Comparativa Global de Magnitudes
      </h3>
      <div className="h-64 w-full text-xs font-mono">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={dataGrafico} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" stroke="#64748b" />
            <YAxis dataKey="name" type="category" stroke="#64748b" width={90} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
              formatter={(value, name, props) => [`${value} ${props.payload.unidad}`, 'Lectura']}
            />
            <Bar dataKey="Valor" fill="#38bdf8" radius={[0, 4, 4, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default GraficoSensores

GraficoSensores.propTypes = {
  datos: PropTypes.arrayOf(
    PropTypes.shape({
      codigo_sensor: PropTypes.string.isRequired,
      valor: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      unidad_medida: PropTypes.string,
    })
  ).isRequired,
}