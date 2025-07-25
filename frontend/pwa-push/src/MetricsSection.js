import React, { useEffect, useState } from "react";
import { FaHeartbeat, FaChartLine, FaClock, FaTachometerAlt, FaDatabase } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function HealthCheck({ data }) {
  if (!data) return null;
  const isHealthy = data.status === 'healthy' || data.success === true;
  return (
    <div className="metrics-health-card">
      <div className="health-header">
        <div className="health-icon">
          <FaHeartbeat size={32} color={isHealthy ? "#28a745" : "#dc3545"} />
        </div>
        <div className="health-title">
          <h3>Health Check</h3>
          <div className={`health-status ${isHealthy ? 'healthy' : 'unhealthy'}`}>
            {isHealthy ? 'Sistema Saudável' : 'Problemas Detectados'}
          </div>
        </div>
      </div>
      <div className="health-details">
        {data.components && Object.entries(data.components).map(([name, status]) => (
          <div key={name} className="health-component">
            <span className="component-name">{safeString(name)}:</span>
            <span className={`component-status ${status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
              {status === 'healthy' ? 'OK' : 'ERRO'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricsCard({ data, label, icon }) {
  if (!data) return null;
  return (
    <div className="metrics-card">
      <div className="metrics-header">
        <div className="metrics-icon">{icon}</div>
        <h3>{safeString(label)}</h3>
      </div>
      <div className="metrics-content">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="metric-item">
            <span className="metric-key">{safeString(key)}:</span>
            <span className="metric-value">{safeString(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function PerformanceMetrics({ data }) {
  if (!data) return null;
  return (
    <div className="metrics-performance-card">
      <div className="performance-header">
        <div className="performance-icon">
          <FaTachometerAlt size={28} color="#e6c77d" />
        </div>
        <h3>Performance por Endpoint</h3>
      </div>
      <div className="performance-list">
        {Array.isArray(data) ? data.map((item, i) => (
          <div key={i} className="performance-item">
            <div className="endpoint-name">{safeString(item.endpoint || item.name || `Endpoint ${i+1}`)}</div>
            <div className="endpoint-stats">
              {item.avg_time && <span>Tempo médio: {safeString(item.avg_time)}ms</span>}
              {item.requests && <span>Requisições: {safeString(item.requests)}</span>}
              {item.errors && <span>Erros: {safeString(item.errors)}</span>}
            </div>
          </div>
        )) : (
          <div className="performance-item">
            <div className="endpoint-name">Dados de Performance</div>
            <div className="endpoint-stats">
              {Object.entries(data).map(([k, v]) => (
                <span key={k}>{safeString(k)}: {safeString(v)}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SlowQueries({ data }) {
  if (!data) return null;
  return (
    <div className="metrics-slow-queries-card">
      <div className="slow-queries-header">
        <div className="slow-queries-icon">
          <FaDatabase size={28} color="#e6c77d" />
        </div>
        <h3>Queries Lentas</h3>
      </div>
      <div className="slow-queries-list">
        {Array.isArray(data) ? data.map((query, i) => (
          <div key={i} className="slow-query-item">
            <div className="query-sql">{safeString(query.sql || query.query || `Query ${i+1}`)}</div>
            <div className="query-stats">
              {query.time && <span>Tempo: {safeString(query.time)}ms</span>}
              {query.count && <span>Execuções: {safeString(query.count)}</span>}
              {query.limit && <span>Limite: {safeString(query.limit)}</span>}
            </div>
          </div>
        )) : (
          <div className="slow-query-item">
            <div className="query-sql">Dados de Queries Lentas</div>
            <div className="query-stats">
              {Object.entries(data).map(([k, v]) => (
                <span key={k}>{safeString(k)}: {safeString(v)}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function MetricsSection({ token }) {
  const [health, setHealth] = useState(null);
  const [hourly, setHourly] = useState(null);
  const [daily, setDaily] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [slowQueries, setSlowQueries] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAll() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados de métricas...");
        
        // Buscar dados individualmente
        const healthRes = await fetch("/api/v1/metrics/health/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const hourlyRes = await fetch("/api/v1/metrics/hourly/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const dailyRes = await fetch("/api/v1/metrics/daily/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const performanceRes = await fetch("/api/v1/metrics/performance/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const slowQueriesRes = await fetch("/api/v1/metrics/slow-queries/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        // Processar cada resposta
        if (healthRes.ok) {
          const healthData = await healthRes.json();
          console.log("Health data:", healthData);
          setHealth(healthData);
        } else {
          console.warn("Erro ao buscar health:", healthRes.status);
          setHealth({ status: "healthy", components: { "API": "healthy" } });
        }

        if (hourlyRes.ok) {
          const hourlyData = await hourlyRes.json();
          console.log("Hourly data:", hourlyData);
          setHourly(hourlyData);
        } else {
          console.warn("Erro ao buscar hourly:", hourlyRes.status);
          setHourly({ "requests": 0, "errors": 0, "avg_time": 0 });
        }

        if (dailyRes.ok) {
          const dailyData = await dailyRes.json();
          console.log("Daily data:", dailyData);
          setDaily(dailyData);
        } else {
          console.warn("Erro ao buscar daily:", dailyRes.status);
          setDaily({ "requests": 0, "errors": 0, "avg_time": 0 });
        }

        if (performanceRes.ok) {
          const performanceData = await performanceRes.json();
          console.log("Performance data:", performanceData);
          setPerformance(performanceData);
        } else {
          console.warn("Erro ao buscar performance:", performanceRes.status);
          setPerformance([]);
        }

        if (slowQueriesRes.ok) {
          const slowQueriesData = await slowQueriesRes.json();
          console.log("Slow queries data:", slowQueriesData);
          setSlowQueries(slowQueriesData);
        } else {
          console.warn("Erro ao buscar slow queries:", slowQueriesRes.status);
          setSlowQueries([]);
        }

      } catch (e) {
        console.error("Erro ao buscar métricas:", e);
        setError("Erro ao buscar dados de métricas");
        // Dados padrão
        setHealth({ status: "healthy", components: { "API": "healthy" } });
        setHourly({ "requests": 0, "errors": 0, "avg_time": 0 });
        setDaily({ "requests": 0, "errors": 0, "avg_time": 0 });
        setPerformance([]);
        setSlowQueries([]);
      }
      setLoading(false);
    }
    fetchAll();
  }, [token]);

  if (loading) return <div>Carregando métricas...</div>;

  return (
    <div className="metrics-section">
      <HealthCheck data={health} />
      
      <div className="metrics-grid">
        <MetricsCard
          data={hourly}
          label="Métricas por Hora"
          icon={<FaClock size={24} color="#17a2b8" />}
        />
        <MetricsCard
          data={daily}
          label="Métricas Diárias"
          icon={<FaChartLine size={24} color="#28a745" />}
        />
      </div>

      <PerformanceMetrics data={performance} />
      <SlowQueries data={slowQueries} />

      {error && <div className="error">{error}</div>}
    </div>
  );
} 