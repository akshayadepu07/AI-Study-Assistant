// Provider list + default model + key-help links all come from the
// backend (GET /api/providers) so this file never needs to be edited
// when a provider's default model changes — only app/ai_providers.py
// on the backend does.
import { useEffect, useState } from "react";
import { fetchProviders } from "../api.js";

export default function ProviderSelector({ provider, onChange }) {
  const [providers, setProviders] = useState([]);

  useEffect(() => {
    fetchProviders()
      .then((list) => {
        setProviders(list);
        // If nothing selected yet, default to the first provider (Groq — free & fast)
        if (!provider && list.length > 0) onChange(list[0].id);
      })
      .catch(() => {
        /* backend not reachable yet — dropdown stays empty until it is */
      });
  }, []);

  return (
    <label className="provider-selector">
      Provider
      <select value={provider} onChange={(e) => onChange(e.target.value)}>
        {providers.length === 0 && <option value="">Loading…</option>}
        {providers.map((p) => (
          <option key={p.id} value={p.id}>
            {p.label}
          </option>
        ))}
      </select>
    </label>
  );
}
