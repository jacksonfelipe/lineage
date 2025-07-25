import React, { useState, useEffect } from "react";
import { FaCrown, FaUsers, FaGem, FaCoins, FaSword, FaShieldAlt, FaSearch, FaSync, FaCalendar, FaMapMarkerAlt, FaStar, FaGavel, FaClock, FaUser, FaTag, FaChartBar } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Função para formatar data
function formatDate(dateString) {
  if (!dateString) return "N/A";
  try {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  } catch (e) {
    return dateString;
  }
}

// Função para formatar números
function formatNumber(num) {
  if (num === null || num === undefined) return "0";
  if (typeof num === 'string') return num;
  return num.toLocaleString('pt-BR');
}

function ClanCard({ data }) {
  if (!data) return null;

  const clanStats = [
    { key: "level", label: "Level", icon: <FaStar size={16} />, color: "#ffc107" },
    { key: "members", label: "Membros", icon: <FaUsers size={16} />, color: "#17a2b8" },
    { key: "reputation", label: "Reputação", icon: <FaShieldAlt size={16} />, color: "#28a745" }
  ];

  return (
    <div className="clan-card">
      <div className="clan-header">
        <div className="clan-icon">
          <FaCrown size={32} color="#e6c77d" />
        </div>
        <div className="clan-info">
          <h3>{safeString(data.name || data.clan_name || "Clã")}</h3>
          <div className="clan-leader">
            <FaUser size={14} color="#6c757d" />
            <span>{safeString(data.leader || data.clan_leader || "Líder desconhecido")}</span>
          </div>
        </div>
        <div className="clan-badge">
          <FaCrown size={16} color="#e6c77d" />
        </div>
      </div>
      
      <div className="clan-stats">
        {clanStats.map(stat => (
          data[stat.key] && (
            <div key={stat.key} className="clan-stat-item" style={{ borderColor: stat.color }}>
              <div className="stat-icon" style={{ color: stat.color }}>
                {stat.icon}
              </div>
              <div className="stat-info">
                <span className="stat-label">{stat.label}</span>
                <span className="stat-value">{formatNumber(data[stat.key])}</span>
              </div>
            </div>
          )
        ))}
      </div>

      <div className="clan-details">
        {data.alliance && (
          <div className="clan-detail-item">
            <FaUsers size={14} color="#6c757d" />
            <span className="detail-label">Aliança:</span>
            <span className="detail-value">{safeString(data.alliance)}</span>
          </div>
        )}
        {data.territory && (
          <div className="clan-detail-item">
            <FaMapMarkerAlt size={14} color="#6c757d" />
            <span className="detail-label">Território:</span>
            <span className="detail-value">{safeString(data.territory)}</span>
          </div>
        )}
        {data.creation_date && (
          <div className="clan-detail-item">
            <FaCalendar size={14} color="#6c757d" />
            <span className="detail-label">Criado em:</span>
            <span className="detail-value">{formatDate(data.creation_date)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function AuctionGrid({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="auction-empty">
        <div className="empty-icon">🏪</div>
        <p>Nenhum item disponível no leilão</p>
        <span className="empty-subtitle">Os itens aparecerão aqui quando disponíveis</span>
      </div>
    );
  }

  return (
    <div className="auction-grid">
      {data.map((item, i) => (
        <div className="auction-card" key={i}>
          <div className="auction-header">
            <div className="auction-icon">
              <FaGem size={20} color="#e6c77d" />
            </div>
            <div className="auction-name">{safeString(item.name || item.item_name || "Item")}</div>
            <div className="auction-price">
              <FaCoins size={14} color="#ffc107" />
              <span>{formatNumber(item.price || 0)}</span>
            </div>
          </div>
          
          <div className="auction-details">
            {item.seller && (
              <div className="auction-detail-item">
                <FaUser size={12} color="#6c757d" />
                <span className="detail-label">Vendedor:</span>
                <span className="detail-value">{safeString(item.seller)}</span>
              </div>
            )}
            {item.quantity && (
              <div className="auction-detail-item">
                <FaTag size={12} color="#6c757d" />
                <span className="detail-label">Quantidade:</span>
                <span className="detail-value">{formatNumber(item.quantity)}</span>
              </div>
            )}
            {item.end_time && (
              <div className="auction-detail-item">
                <FaClock size={12} color="#6c757d" />
                <span className="detail-label">Termina:</span>
                <span className="detail-value">{formatDate(item.end_time)}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function GameStats({ stats }) {
  if (!stats || Object.keys(stats).length === 0) {
    return (
      <div className="game-stats-section">
        <div className="stats-header">
          <FaChartBar size={20} color="#e6c77d" />
          <h3>Estatísticas do Jogo</h3>
        </div>
        <div className="stats-empty">
          <div className="empty-icon">📊</div>
          <p>Nenhuma estatística disponível</p>
        </div>
      </div>
    );
  }

  const statItems = [
    { key: "total_players", label: "Total de Jogadores", icon: <FaUsers size={16} />, color: "#17a2b8" },
    { key: "online_players", label: "Jogadores Online", icon: <FaUsers size={16} />, color: "#28a745" },
    { key: "total_clans", label: "Total de Clãs", icon: <FaCrown size={16} />, color: "#e6c77d" },
    { key: "active_auctions", label: "Leilões Ativos", icon: <FaGavel size={16} />, color: "#fd7e14" }
  ];

  return (
    <div className="game-stats-section">
      <div className="stats-header">
        <FaChartBar size={20} color="#e6c77d" />
        <h3>Estatísticas do Jogo</h3>
      </div>
      <div className="stats-grid">
        {statItems.map(stat => (
          stats[stat.key] && (
            <div key={stat.key} className="stat-card" style={{ borderColor: stat.color }}>
              <div className="stat-icon" style={{ color: stat.color }}>
                {stat.icon}
              </div>
              <div className="stat-info">
                <span className="stat-label">{stat.label}</span>
                <span className="stat-value">{formatNumber(stats[stat.key])}</span>
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
}

export default function GameSection({ token }) {
  const [clanName, setClanName] = useState("");
  const [clanData, setClanData] = useState(null);
  const [auctionItems, setAuctionItems] = useState(null);
  const [gameStats, setGameStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchGameData();
  }, [token]);

  async function fetchGameData() {
    setLoading(true);
    setError("");
    try {
      console.log("Buscando dados do jogo...");
      
      // Buscar dados individualmente
      const auctionRes = await fetch("/api/v1/auction/items/", {
        headers: { Authorization: `Bearer ${token}` }
      });
      const statsRes = await fetch("/api/v1/game/stats/", {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Processar cada resposta
      if (auctionRes.ok) {
        const auctionData = await auctionRes.json();
        console.log("Auction data:", auctionData);
        setAuctionItems(auctionData);
      } else {
        console.warn("Erro ao buscar leilão:", auctionRes.status);
        setAuctionItems([]);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        console.log("Game stats data:", statsData);
        setGameStats(statsData);
      } else {
        console.warn("Erro ao buscar estatísticas:", statsRes.status);
        setGameStats({});
      }

    } catch (e) {
      console.error("Erro ao buscar dados do jogo:", e);
      setError("Erro ao buscar dados do jogo");
      setAuctionItems([]);
      setGameStats({});
    }
    setLoading(false);
  }

  async function searchClan(e) {
    e.preventDefault();
    if (!clanName.trim()) return;
    
    setSearching(true);
    setError("");
    try {
      const res = await fetch(`/api/v1/clan/${encodeURIComponent(clanName)}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setClanData(data);
    } catch (e) {
      setError("Erro ao buscar clã");
    }
    setSearching(false);
  }

  if (loading) return <div className="loading">Carregando dados do jogo...</div>;

  return (
    <div className="game-section">
      {/* Estatísticas do Jogo */}
      <GameStats stats={gameStats} />

      {/* Busca de Clã */}
      <div className="game-clan-section">
        <div className="clan-header-section">
          <FaCrown size={24} color="#e6c77d" />
          <h3>Busca de Clã</h3>
        </div>
        <div className="clan-search-box">
          <form onSubmit={searchClan} className="clan-search-form">
            <div className="search-input-group">
              <FaSearch size={16} color="#6c757d" />
              <input
                type="text"
                placeholder="Digite o nome do clã..."
                value={clanName}
                onChange={e => setClanName(e.target.value)}
                className="search-input"
                required
              />
            </div>
            <button className="btn-primary" type="submit" disabled={searching}>
              {searching ? "Buscando..." : "Buscar Clã"}
            </button>
          </form>
          {clanData && <ClanCard data={clanData} />}
        </div>
      </div>

      {/* Itens do Leilão */}
      <div className="game-auction-section">
        <div className="auction-header-section">
          <div className="auction-title">
            <FaGavel size={24} color="#e6c77d" />
            <h3>Itens do Leilão</h3>
          </div>
          <button className="btn-secondary refresh-btn" onClick={fetchGameData} disabled={loading}>
            <FaSync size={14} />
            {loading ? "Carregando..." : "Atualizar"}
          </button>
        </div>
        <div className="auction-content">
          <AuctionGrid data={auctionItems} />
        </div>
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
} 