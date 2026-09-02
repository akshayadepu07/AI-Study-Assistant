const BASE = import.meta.env.VITE_API_BASE_URL || "";

function authHeaders() {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function sendChatMessage({ sessionId, message, provider, apiKey }) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      provider,
      api_key: apiKey,
    }),
  });
  return handle(res);
}

export async function listSessions() {
  const res = await fetch(`${BASE}/api/sessions`, { headers: authHeaders() });
  return handle(res);
}

export async function getSession(sessionId) {
  const res = await fetch(`${BASE}/api/sessions/${sessionId}`, { headers: authHeaders() });
  return handle(res);
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${BASE}/api/sessions/${sessionId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  return handle(res);
}

export async function sendFeedback({ messageId, rating, comment }) {
  const res = await fetch(`${BASE}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ message_id: messageId, rating, comment }),
  });
  return handle(res);
}

export async function fetchProviders() {
  const res = await fetch(`${BASE}/api/providers`);
  return handle(res);
}

export async function googleLogin(credential) {
  const res = await fetch(`${BASE}/api/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential }),
  });
  return handle(res);
}

export async function fetchMe() {
  const res = await fetch(`${BASE}/api/auth/me`, { headers: authHeaders() });
  return handle(res);
}