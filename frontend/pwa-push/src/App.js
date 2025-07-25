import React, { useState } from "react";
import { subscribeUserToPush, unsubscribeUserFromPush } from "./push";
import "./App.css";

export default function App() {
  const [permission, setPermission] = useState(Notification.permission);
  const [subscribed, setSubscribed] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("jwt_token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const res = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.access) {
        setToken(data.access);
        localStorage.setItem("jwt_token", data.access);
      } else {
        setLoginError(data.detail || "Usuário ou senha inválidos");
      }
    } catch (err) {
      setLoginError("Erro ao conectar ao servidor");
    }
    setLoading(false);
  };

  const handleSubscribe = async () => {
    console.log("Clicou em Ativar Push");
    const result = await subscribeUserToPush(token);
    console.log("Resultado subscribeUserToPush:", result);
    if (result) {
      setSubscribed(true);
      setPermission("granted");
    }
  };

  const handleUnsubscribe = async () => {
    if (!('serviceWorker' in navigator)) return;
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await subscription.unsubscribe();
      await unsubscribeUserFromPush(token, subscription);
      setSubscribed(false);
      setPermission(Notification.permission);
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("jwt_token");
    setSubscribed(false);
    setUsername("");
    setPassword("");
  };

  if (!token) {
    return (
      <div className="pwa-container">
        <img src="/static/pwa/icons/logo.png" alt="Logo" className="logo" />
        <h1>Login</h1>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="input"
            autoFocus
            required
          />
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="input"
            required
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
        {loginError && <p className="error">{loginError}</p>}
      </div>
    );
  }

  if (subscribed) {
    return (
      <div className="pwa-container">
        <img src="/static/pwa/icons/logo.png" alt="Logo" className="logo" />
        <h1>Notificações Ativadas!</h1>
        <p className="success">Você receberá alertas importantes deste app.</p>
        <p>Você pode fechar este app, as notificações chegarão normalmente.</p>
        <hr />
        <p className="install-tip">
          Para instalar, use o menu do navegador e escolha <b>“Adicionar à tela inicial”</b>.
        </p>
        <button className="btn-primary" onClick={handleUnsubscribe} style={{marginTop: 16}}>Desativar Push</button>
        <button className="btn-secondary" onClick={handleLogout} style={{marginTop: 8}}>Sair</button>
      </div>
    );
  }

  return (
    <div className="pwa-container">
      <img src="/static/pwa/icons/logo.png" alt="Logo" className="logo" />
      <h1>Notificações Push</h1>
      <p>Receba alertas importantes diretamente no seu celular.</p>
      {permission !== "granted" && (
        <button className="btn-primary" onClick={handleSubscribe}>
          Permitir Notificações
        </button>
      )}
      {permission === "granted" && !subscribed && (
        <button className="btn-primary" onClick={handleSubscribe}>
          Ativar Push
        </button>
      )}
      <hr />
      <p className="install-tip">
        Para instalar, use o menu do navegador e escolha <b>“Adicionar à tela inicial”</b>.
      </p>
      <button className="btn-secondary" onClick={handleLogout} style={{marginTop: 16}}>Sair</button>
    </div>
  );
} 