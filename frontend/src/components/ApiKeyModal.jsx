import { useEffect, useState } from "react";
import { fetchProviders } from "../api.js";

// Keys are stored ONLY in the browser's localStorage, per provider,
// and sent straight to our backend -> straight to the AI provider.
// They are never written to our MySQL database.
const STORAGE_PREFIX = "ai_study_assistant_key_";

export function getStoredKey(provider) {
  return localStorage.getItem(STORAGE_PREFIX + provider) || "";
}

export function storeKey(provider, key) {
  localStorage.setItem(STORAGE_PREFIX + provider, key);
}

export default function ApiKeyModal({ provider, onClose, onSaved }) {
  const [key, setKey] = useState(getStoredKey(provider));
  const [cfg, setCfg] = useState(null);

  useEffect(() => {
    fetchProviders().then((list) => {
      setCfg(list.find((p) => p.id === provider) || null);
    });
  }, [provider]);

  if (!cfg) return null; // brief flash while /api/providers loads

  function handleSave() {
    storeKey(provider, key.trim());
    onSaved(key.trim());
    onClose();
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Add your {cfg.label} API key</h3>
        <p className="modal-hint">
          {cfg.key_hint} Your key stays in your browser and is only
          forwarded to {cfg.label} to generate replies — we never store it.
          Answers will come from <code>{cfg.default_model}</code>.
        </p>

        <input
          type="password"
          placeholder="Paste your API key here"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          autoFocus
        />

        <a href={cfg.key_link} target="_blank" rel="noreferrer">
          Don't have a key? Get one from {cfg.label} →
        </a>

        <div className="modal-actions">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} className="btn-primary" disabled={!key.trim()}>
            Save key
          </button>
        </div>
      </div>
    </div>
  );
}
