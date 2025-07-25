import React, { useEffect, useState } from "react";
import { FaUserCircle } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export default function UserSection({ token }) {
  const [profile, setProfile] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [changeMsg, setChangeMsg] = useState("");
  const [changing, setChanging] = useState(false);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados do usuário...");
        
        // Buscar dados individualmente para evitar que um erro quebre tudo
        const profileRes = await fetch("/api/v1/user/profile/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const dashboardRes = await fetch("/api/v1/user/dashboard/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const statsRes = await fetch("/api/v1/user/stats/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        // Processar cada resposta individualmente
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          console.log("Profile data:", profileData);
          setProfile(profileData);
        } else {
          console.warn("Erro ao buscar perfil:", profileRes.status);
          setProfile({ name: "Usuário", email: "email@exemplo.com" });
        }

        if (dashboardRes.ok) {
          const dashboardData = await dashboardRes.json();
          console.log("Dashboard data:", dashboardData);
          setDashboard(dashboardData);
        } else {
          console.warn("Erro ao buscar dashboard:", dashboardRes.status);
          setDashboard({ "Último login": "Hoje", "Status": "Ativo" });
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          console.log("Stats data:", statsData);
          setStats(statsData);
        } else {
          console.warn("Erro ao buscar estatísticas:", statsRes.status);
          setStats({ "Total de logins": "0", "Dias ativo": "0" });
        }

      } catch (e) {
        console.error("Erro ao buscar dados:", e);
        setError("Erro ao buscar dados do usuário");
        // Definir dados padrão em caso de erro
        setProfile({ name: "Usuário", email: "email@exemplo.com" });
        setDashboard({ "Último login": "Hoje", "Status": "Ativo" });
        setStats({ "Total de logins": "0", "Dias ativo": "0" });
      }
      setLoading(false);
    }
    fetchData();
  }, [token]);

  async function handleChangePassword(e) {
    e.preventDefault();
    setChanging(true);
    setChangeMsg("");
    try {
      const res = await fetch("/api/v1/user/change-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ new_password: password, new_password2: password2 })
      });
      const data = await res.json();
      if (res.ok) {
        setChangeMsg("Senha alterada com sucesso!");
        setPassword("");
        setPassword2("");
      } else {
        setChangeMsg(data.detail || "Erro ao alterar senha");
      }
    } catch (e) {
      setChangeMsg("Erro ao conectar ao servidor");
    }
    setChanging(false);
  }

  if (loading) return <div>Carregando dados do usuário...</div>;

  return (
    <div className="user-section">
      <div className="user-profile-card">
        <div className="user-avatar">
          <FaUserCircle size={64} color="#e6c77d" />
        </div>
        <div className="user-info">
          <h2>{safeString(profile?.name || profile?.username || "Usuário")}</h2>
          <p>{safeString(profile?.email || "email@exemplo.com")}</p>
        </div>
      </div>
      <div className="user-dashboard-stats">
        <div className="user-dashboard-box">
          <h3>Dashboard</h3>
          <ul>
            {dashboard && Object.entries(dashboard).map(([k, v]) => (
              <li key={k}>
                <span className="stat-key">{safeString(k)}:</span> 
                <span className="stat-value">{safeString(v)}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="user-stats-box">
          <h3>Estatísticas</h3>
          <ul>
            {stats && Object.entries(stats).map(([k, v]) => (
              <li key={k}>
                <span className="stat-key">{safeString(k)}:</span> 
                <span className="stat-value">{safeString(v)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="user-password-box">
        <h3>Alterar Senha</h3>
        <form onSubmit={handleChangePassword} className="user-password-form">
          <input
            type="password"
            placeholder="Nova senha"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Confirmar nova senha"
            value={password2}
            onChange={e => setPassword2(e.target.value)}
            required
          />
          <button type="submit" disabled={changing}>
            {changing ? "Alterando..." : "Alterar Senha"}
          </button>
        </form>
        {changeMsg && <p className={changeMsg.includes("sucesso") ? "success" : "error"}>{changeMsg}</p>}
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
} 