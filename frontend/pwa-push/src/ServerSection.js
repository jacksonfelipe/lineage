import React, { useEffect, useState } from "react";
import { FaServer, FaUsers, FaTrophy, FaSkull, FaFlag, FaCheck, FaTimes, FaClock, FaCode, FaCrown, FaDragon } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Função para formatar uptime
function formatUptime(uptime) {
  if (!uptime) return "0h";
  if (typeof uptime === 'string') return uptime;
  if (typeof uptime === 'number') {
    const hours = Math.floor(uptime / 3600);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days}d ${hours % 24}h`;
    return `${hours}h`;
  }
  return uptime;
}

function RankingTable({ title, data, icon, emptyMessage = "Nenhum ranking disponível" }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="ranking-table">
        <div className="ranking-header">
          <div className="ranking-icon">{icon}</div>
          <h3>{title}</h3>
        </div>
        <div className="ranking-empty">
          <div className="empty-icon">🏆</div>
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ranking-table">
      <div className="ranking-header">
        <div className="ranking-icon">{icon}</div>
        <h3>{title}</h3>
        <span className="ranking-count">{data.length} jogadores</span>
      </div>
      <div className="ranking-content">
        <table>
          <thead>
            <tr>
              <th>Pos</th>
              <th>Nome</th>
              <th>Pontos</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 10).map((item, i) => (
              <tr key={i} className={i < 3 ? `top-${i + 1}` : ''}>
                <td className="position">
                  {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                </td>
                <td className="player-name">{safeString(item.name || item.character_name || "Desconhecido")}</td>
                <td className="player-points">{safeString(item.points || item.level || "0")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusCard({ title, value, icon, color = "#e6c77d", subtitle = "" }) {
  return (
    <div className="status-card" style={{ borderColor: color }}>
      <div className="status-icon" style={{ color }}>
        {icon}
      </div>
      <div className="status-info">
        <h3>{safeString(title)}</h3>
        <p className="status-value">{safeString(value)}</p>
        {subtitle && <p className="status-subtitle">{subtitle}</p>}
      </div>
    </div>
  );
}

function BossGrid({ bosses }) {
  if (!Array.isArray(bosses) || bosses.length === 0) {
    return (
      <div className="boss-grid">
        <div className="boss-header">
          <FaDragon size={24} color="#e6c77d" />
          <h3>Status dos Bosses</h3>
        </div>
        <div className="boss-empty">
          <div className="empty-icon">🐉</div>
          <p>Nenhum boss disponível</p>
        </div>
      </div>
    );
  }

  return (
    <div className="boss-grid">
      <div className="boss-header">
        <FaDragon size={24} color="#e6c77d" />
        <h3>Status dos Bosses</h3>
        <span className="boss-count">{bosses.length} bosses</span>
      </div>
      <div className="boss-cards">
        {bosses.map((boss, i) => (
          <div key={i} className={`boss-card ${boss.alive ? 'alive' : 'dead'}`}>
            <div className="boss-status">
              {boss.alive ? <FaCheck color="green" size={20} /> : <FaTimes color="red" size={20} />}
            </div>
            <div className="boss-info">
              <h4>{safeString(boss.name || "Boss")}</h4>
              <p className={`boss-state ${boss.alive ? 'alive' : 'dead'}`}>
                {boss.alive ? "Vivo" : "Morto"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SiegeInfo({ siege }) {
  if (!siege) return null;

  return (
    <div className="siege-info">
      <div className="siege-header">
        <FaCrown size={24} color="#e6c77d" />
        <h3>Informações do Siege</h3>
      </div>
      <div className="siege-card">
        <div className="siege-status">
          <div className="siege-item">
            <span className="siege-label">Status:</span>
            <span className={`siege-value ${siege.active ? 'active' : 'inactive'}`}>
              {siege.active ? "Ativo" : "Inativo"}
            </span>
          </div>
          <div className="siege-item">
            <span className="siege-label">Castle:</span>
            <span className="siege-value">{safeString(siege.castle || "Nenhum")}</span>
          </div>
          <div className="siege-item">
            <span className="siege-label">Guild:</span>
            <span className="siege-value">{safeString(siege.guild || "Nenhuma")}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ServerSection({ token }) {
  const [status, setStatus] = useState(null);
  const [rankings, setRankings] = useState({});
  const [bosses, setBosses] = useState([]);
  const [siege, setSiege] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados do servidor...");
        
        // Buscar dados individualmente
        const statusRes = await fetch("/api/v1/server/status/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topLevelRes = await fetch("/api/v1/server/top-level/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topPvpRes = await fetch("/api/v1/server/top-pvp/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topClanRes = await fetch("/api/v1/server/top-clan/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const grandBossRes = await fetch("/api/v1/server/grandboss-status/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const siegeRes = await fetch("/api/v1/server/siege/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        // Processar cada resposta
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          console.log("Status data:", statusData);
          setStatus(statusData);
        } else {
          console.warn("Erro ao buscar status:", statusRes.status);
          setStatus({ 
            online: false, 
            players: 0, 
            uptime: 0, 
            version: "1.0.0" 
          });
        }

        if (topLevelRes.ok) {
          const topLevelData = await topLevelRes.json();
          console.log("Top level data:", topLevelData);
          setRankings(prev => ({ ...prev, level: topLevelData }));
        } else {
          console.warn("Erro ao buscar top level:", topLevelRes.status);
          setRankings(prev => ({ ...prev, level: [] }));
        }

        if (topPvpRes.ok) {
          const topPvpData = await topPvpRes.json();
          console.log("Top PvP data:", topPvpData);
          setRankings(prev => ({ ...prev, pvp: topPvpData }));
        } else {
          console.warn("Erro ao buscar top PvP:", topPvpRes.status);
          setRankings(prev => ({ ...prev, pvp: [] }));
        }

        if (topClanRes.ok) {
          const topClanData = await topClanRes.json();
          console.log("Top clan data:", topClanData);
          setRankings(prev => ({ ...prev, guild: topClanData }));
        } else {
          console.warn("Erro ao buscar top clan:", topClanRes.status);
          setRankings(prev => ({ ...prev, guild: [] }));
        }

        // Buscar status dos bosses
        if (grandBossRes.ok) {
          const grandBossData = await grandBossRes.json();
          console.log("Grand boss data:", grandBossData);
          setBosses(grandBossData);
        } else {
          console.warn("Erro ao buscar grand boss:", grandBossRes.status);
          setBosses([
            { name: "Boss 1", alive: true },
            { name: "Boss 2", alive: false }
          ]);
        }

        if (siegeRes.ok) {
          const siegeData = await siegeRes.json();
          console.log("Siege data:", siegeData);
          setSiege(siegeData);
        } else {
          console.warn("Erro ao buscar siege:", siegeRes.status);
          setSiege({ 
            active: false, 
            castle: "", 
            guild: "" 
          });
        }

      } catch (e) {
        console.error("Erro ao buscar dados do servidor:", e);
        setError("Erro ao buscar dados do servidor");
        // Dados padrão
        setStatus({ online: false, players: 0, uptime: 0, version: "1.0.0" });
        setRankings({ level: [], pvp: [], guild: [] });
        setBosses([{ name: "Boss 1", alive: true }, { name: "Boss 2", alive: false }]);
        setSiege({ active: false, castle: "", guild: "" });
      }
      setLoading(false);
    }
    fetchData();
  }, [token]);

  if (loading) return <div className="loading">Carregando dados do servidor...</div>;

  return (
    <div className="server-section">
      {/* Status Cards */}
      <div className="server-status-cards">
        <StatusCard
          title="Status"
          value={status?.online ? "Online" : "Offline"}
          icon={<FaServer size={24} />}
          color={status?.online ? "#28a745" : "#dc3545"}
          subtitle={status?.online ? "Servidor funcionando" : "Servidor indisponível"}
        />
        <StatusCard
          title="Jogadores"
          value={status?.players || "0"}
          icon={<FaUsers size={24} />}
          color="#17a2b8"
          subtitle="jogadores online"
        />
        <StatusCard
          title="Uptime"
          value={formatUptime(status?.uptime)}
          icon={<FaClock size={24} />}
          color="#ffc107"
          subtitle="tempo ativo"
        />
        <StatusCard
          title="Versão"
          value={status?.version || "1.0.0"}
          icon={<FaCode size={24} />}
          color="#6c757d"
          subtitle="versão atual"
        />
      </div>

      {/* Rankings */}
      <div className="server-rankings">
        <RankingTable
          title="Ranking de Level"
          data={rankings.level || []}
          icon={<FaTrophy />}
          emptyMessage="Nenhum ranking de level disponível"
        />
        <RankingTable
          title="Ranking PvP"
          data={rankings.pvp || []}
          icon={<FaSkull />}
          emptyMessage="Nenhum ranking PvP disponível"
        />
        <RankingTable
          title="Ranking de Guild"
          data={rankings.guild || []}
          icon={<FaFlag />}
          emptyMessage="Nenhum ranking de guild disponível"
        />
      </div>

      {/* Bosses */}
      <BossGrid bosses={bosses} />

      {/* Siege */}
      <SiegeInfo siege={siege} />

      {error && <div className="error">{error}</div>}
    </div>
  );
} 