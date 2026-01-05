import { useState } from "react";

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = e => {
    e.preventDefault();
    if (username === "admin" && password === "admin123") {
      onLogin();
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: "2rem auto" }}>
      <h2>Admin Login</h2>
      <input className="form-control mb-2" type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
      <input className="form-control mb-2" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <button className="btn btn-primary w-100" type="submit">Login</button>
    </form>
  );
};

export default LoginForm;