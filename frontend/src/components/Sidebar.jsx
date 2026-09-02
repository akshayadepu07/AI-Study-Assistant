import { useEffect, useRef, useState } from "react";
import ProviderSelector from "./ProviderSelector.jsx";

export default function Sidebar({
  sessions,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  user,
  onSignOut,
  provider,
  onProviderChange,
  apiKey,
  onOpenKeyModal,
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <aside className="sidebar">
      <button className="btn-primary new-chat-btn" onClick={onNewChat}>
        + New chat
      </button>

      <div className="session-list">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={`session-item ${s.id === activeId ? "session-item-active" : ""}`}
          >
            <span onClick={() => onSelect(s.id)} className="session-title">
              {s.title || "Untitled chat"}
            </span>
            <button
              className="session-delete"
              title="Delete chat"
              onClick={() => onDelete(s.id)}
            >
              ×
            </button>
          </div>
        ))}
        {sessions.length === 0 && <p className="empty-hint">No chats yet</p>}
      </div>

      <div className="account-anchor" ref={menuRef}>
        {menuOpen && (
          <div className="account-popover">
            <div className="account-popover-header">
              {user.picture && <img src={user.picture} alt="" />}
              <div>
                <div className="account-popover-name">{user.name}</div>
                <div className="account-popover-email">{user.email}</div>
              </div>
            </div>

            <div className="account-popover-section">
              <ProviderSelector provider={provider} onChange={onProviderChange} />
            </div>

            <button
              className="account-popover-item"
              onClick={() => {
                onOpenKeyModal();
                setMenuOpen(false);
              }}
            >
              🔑 {apiKey ? "Change key" : "Add API key"}
            </button>

            <button className="account-popover-item account-popover-danger" onClick={onSignOut}>
              Sign out
            </button>
          </div>
        )}

        <button className="account-trigger" onClick={() => setMenuOpen((v) => !v)}>
          {user.picture && <img src={user.picture} alt="" />}
          <span className="account-trigger-name">{user.name}</span>
        </button>
      </div>
    </aside>
  );
}