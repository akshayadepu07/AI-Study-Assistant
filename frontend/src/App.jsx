import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import ApiKeyModal, { getStoredKey } from "./components/ApiKeyModal.jsx";
import LoginScreen from "./components/LoginScreen.jsx";
import {
  sendChatMessage,
  listSessions,
  getSession,
  deleteSession,
  googleLogin,
  fetchMe,
} from "./api.js";

export default function App() {
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [authError, setAuthError] = useState("");

  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [showKeyModal, setShowKeyModal] = useState(false);

  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");
    if (urlToken) {
      localStorage.setItem("auth_token", urlToken);
      window.history.replaceState({}, "", window.location.pathname);
    }

    const token = localStorage.getItem("auth_token");
    if (!token) {
      setAuthChecked(true);
      return;
    }
    fetchMe()
      .then(setUser)
      .catch(() => localStorage.removeItem("auth_token"))
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    if (!user) return;
    refreshSessions();
  }, [user]);

  useEffect(() => {
    if (provider) setApiKey(getStoredKey(provider));
  }, [provider]);

  async function refreshSessions() {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch {
      /* ignore */
    }
  }

  async function handleGoogleLogin(credential) {
    try {
      const res = await googleLogin(credential);
      localStorage.setItem("auth_token", res.token);
      setUser(res.user);
      setAuthError("");
    } catch (err) {
      setAuthError(err.message);
    }
  }

  function handleSignOut() {
    localStorage.removeItem("auth_token");
    setUser(null);
    setSessions([]);
    setMessages([]);
    setActiveId(null);
  }

  function handleNewChat() {
    setActiveId(null);
    setMessages([]);
    setError("");
  }

  async function handleSelectSession(id) {
    setActiveId(id);
    setError("");
    const data = await getSession(id);
    setMessages(data.messages);
    setProvider(data.provider);
  }

  async function handleDeleteSession(id) {
    await deleteSession(id);
    if (id === activeId) handleNewChat();
    refreshSessions();
  }

  async function handleSend(text) {
    if (!apiKey) {
      setShowKeyModal(true);
      return;
    }
    setError("");
    setMessages((prev) => [...prev, { id: `tmp-${Date.now()}`, role: "user", content: text }]);
    setSending(true);
    try {
      const res = await sendChatMessage({
        sessionId: activeId,
        message: text,
        provider,
        apiKey,
      });
      setActiveId(res.session_id);
      setMessages((prev) => [
        ...prev,
        { id: `tmp-${Date.now()}-r`, role: "assistant", content: res.reply },
      ]);
      refreshSessions();
    } catch (err) {
      setError(err.message || "Something went wrong.");
      if (String(err.message).toLowerCase().includes("key")) {
        setShowKeyModal(true);
      }
    } finally {
      setSending(false);
    }
  }

  if (!authChecked) return null;
  if (!user) return <LoginScreen onGoogleLogin={handleGoogleLogin} error={authError} />;

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={handleSelectSession}
        onNewChat={handleNewChat}
        onDelete={handleDeleteSession}
        user={user}
        onSignOut={handleSignOut}
        provider={provider}
        onProviderChange={setProvider}
        apiKey={apiKey}
        onOpenKeyModal={() => setShowKeyModal(true)}
      />

      <main className="main-panel">
        <header className="topbar">
          <h1>AI Study Assistant</h1>
        </header>

        {error && <div className="error-banner">{error}</div>}

        <ChatWindow messages={messages} onSend={handleSend} sending={sending} />
      </main>

      {showKeyModal && (
        <ApiKeyModal
          provider={provider}
          onClose={() => setShowKeyModal(false)}
          onSaved={(key) => setApiKey(key)}
        />
      )}
    </div>
  );
}