import React, { useState, useEffect } from "react";
import { FaCrown, FaUsers, FaGem, FaCoins, FaSword, FaShield } from "react-icons/fa";

function ClanCard({ data }) {
  if (!data) return null;
  return (
    <div className="clan-card">
      <div className="clan-header">
        <div className="clan-icon">
          <FaCrown size={32} color="#e6c77d" />
        </div>
        <div className="clan-title">
          <h3>{data.name || data.clan_name || "Clã"}</h3>
          <div className="clan-leader">{data.leader || data.clan_leader || "Líder desconhecido"}</div>
        </div>
      </div>
      <div className="clan-details">
        {data.level && <div className="clan-stat"><span>Level:</span> {data.level}</div>}
        {data.members && <div className="clan-stat"><span>Membros:</span> {data.members}</div>}
        {data.reputation && <div className="clan-stat"><span>Reputação:</span> {data.reputation}</div>}
        {data.alliance && <div className="clan-stat"><span>Aliança:</span> {data.alliance}</div>}
        {data.territory && <div className="clan-stat"><span>Território:</span> {data.territory}</div>}
        {data.creation_date && <div className="clan-stat"><span>Criado em:</span> {data.creation_date}</div>}
      </div>
    </div>
  );
}

function AuctionGrid({ data }) {
  if (!Array.isArray(data) || data.length === 0) return <div className="empty">Nenhum item disponível no leilão.</div>;
  return (
    <div className="auction-grid">
      {data.map((item, i) => (
        <div className="auction-card" key={i}>
          <div className="auction-icon">
            <FaGem size={24} color="#e6c77d" />
          </div>
          <div className="auction-info">
            <div className="auction-name">{item.name || item.item_name || "Item"}</div>
            <div className="auction-details">
              {item.seller && <span>Vendedor: {item.seller}</span>}
              {item.price && <span>Preço: {item.price}</span>}
              {item.quantity && <span>Quantidade: {item.quantity}</span>}
              {item.end_time && <span>Termina: {item.end_time}</span>}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function GameSection({ token }) {
  const [clanName, setClanName] = useState("");
  const [clanData, setClanData] = useState(null);
  const [auctionItems, setAuctionItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Carregar itens do leilão automaticamente
    fetchAuctionItems();
  }, []);

  async function fetchAuctionItems() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/auction/items/", {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setAuctionItems(data);
    } catch (e) {
      setError("Erro ao buscar itens do leilão");
    }
    setLoading(false);
  }

  async function searchClan(e) {
    e.preventDefault();
    if (!clanName.trim()) return;
    
    setLoading(true);
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
    setLoading(false);
  }

  return (
    <div className="game-section">
      <div className="game-clan-box">
        <h2>Busca de Clã</h2>
        <form onSubmit={searchClan} className="game-search-form">
          <input
            type="text"
            placeholder="Nome do clã"
            value={clanName}
            onChange={e => setClanName(e.target.value)}
            className="input"
            required
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Buscando..." : "Buscar Clã"}
          </button>
        </form>
        {clanData && <ClanCard data={clanData} />}
      </div>

      <div className="game-auction-box">
        <div className="auction-header">
          <h2>Itens do Leilão</h2>
          <button className="btn-secondary" onClick={fetchAuctionItems} disabled={loading}>
            {loading ? "Carregando..." : "Atualizar Itens"}
          </button>
        </div>
        {auctionItems && <AuctionGrid data={auctionItems} />}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
} 