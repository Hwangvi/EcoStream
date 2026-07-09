import { useState, useEffect, useMemo } from 'react';
import { getDashboard, getAlertas, inyectarAnomalia, limpiarAlertas as limpiarAlertasAPI } from '../api/ecoStream';

export function useDashboard() {
  const [sensores, setSensores] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [zonaSeleccionada, setZonaSeleccionada] = useState('TODAS');
  const [filtrarAlertasPorZona, setFiltrarAlertasPorZona] = useState(false);
  const [errorApi, setErrorApi] = useState(false);

  const dispararAnomalia = async () => {
    try {
      await inyectarAnomalia(zonaSeleccionada);
    } catch (err) {
      console.error('Error al inyectar anomalía:', err);
    }
  };

  const limpiarHistorico = async () => {
    try {
      await limpiarAlertasAPI();
      setAlertas([]);
    } catch (err) {
      console.error('Error al limpiar:', err);
    }
  };

  useEffect(() => {
    const consultarBackend = async () => {
      try {
        const [datosDashboard, datosAlertas] = await Promise.all([
          getDashboard(),
          getAlertas(),
        ]);

        setSensores(datosDashboard);
        setAlertas(datosAlertas);
        setErrorApi(false);
      } catch (err) {
        console.error('Error en sincronización:', err);
        setErrorApi(true);
      }
    };

    consultarBackend();
    const intervalo = setInterval(consultarBackend, 2000);
    return () => clearInterval(intervalo);
  }, []);

  const sensoresFiltrados = useMemo(() => {
    if (zonaSeleccionada === 'TODAS') return sensores;
    return sensores.filter((sensor) =>
      sensor.codigo_sensor.includes(`-${zonaSeleccionada}-`)
    );
  }, [sensores, zonaSeleccionada]);

  const alertasFiltradas = useMemo(() => {
    if (!filtrarAlertasPorZona || zonaSeleccionada === 'TODAS') return alertas;
    return alertas.filter((alerta) =>
      alerta.codigo_sensor.includes(`-${zonaSeleccionada}-`)
    );
  }, [alertas, zonaSeleccionada, filtrarAlertasPorZona]);

  const tieneAlertaCentro = useMemo(
    () => alertas.some((a) => a.codigo_sensor.includes('CENTRO')),
    [alertas]
  );

  const tieneAlertaSur = useMemo(
    () => alertas.some((a) => a.codigo_sensor.includes('SUR')),
    [alertas]
  );

  return {
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
  };
}
