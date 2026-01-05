import LoginForm from "../components/LoginForm";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/admin");
  };

  return (
    <div className="container mt-5">
      <LoginForm onLogin={handleLogin} />
    </div>
  );
};

export default Login;