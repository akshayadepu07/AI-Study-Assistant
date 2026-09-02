import { GoogleLogin } from "@react-oauth/google";

export default function LoginScreen({ onGoogleLogin, error }) {
  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>AI Study Assistant</h1>
        <p>Sign in to save your chat history and pick up where you left off.</p>

        <div className="login-options">
          <GoogleLogin
            onSuccess={(res) => onGoogleLogin(res.credential)}
            onError={() => console.error("Google sign-in failed")}
          />
        </div>

        {error && <p className="error-banner">{error}</p>}
      </div>
    </div>
  );
}