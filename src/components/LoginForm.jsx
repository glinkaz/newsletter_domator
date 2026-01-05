import { useState } from "react";
import { API_BASE_URL } from "../config";

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const handleSubmit = async e => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const loginData = {
      username: username,
      password: password,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loginData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("isAuthenticated", "true");

        onLogin(data.user_id);

      } else {
        setError(data.error || "Błąd logowania. Spróbuj ponownie.");
      }

    } catch (err) {
      console.error("Network or Server Error:", err);
      setError("Wystąpił błąd sieci. Upewnij się, że serwer jest uruchomiony.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: "2rem auto", padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Admin Login</h2>

      {error && (
        <div style={{ color: 'red', marginBottom: '1rem', border: '1px solid red', padding: '10px', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      <input
        className="form-control mb-2"
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        disabled={isLoading}
      />
      <input
        className="form-control mb-2"
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        disabled={isLoading}
      />

      <button
        className="btn btn-primary w-100"
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? "Logowanie..." : "Login"}
      </button>

    </form>
  );
};

export default LoginForm;