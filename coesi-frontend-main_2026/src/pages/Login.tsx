import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import routes from "../constants/routes.json";
import HeaderLogin from "../components/headers/headerlogin";
import Footer from "../components/Footer";

import ClipLoader from "react-spinners/ClipLoader";

import GreenButton from "../components/buttons/greenButton";
import { useAuth } from "../contexts/AuthContext";
import "./login.css";

const LoginPage = () => {
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);

  const navigate = useNavigate();
  const { login, user } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    setIsLoggingIn(true);
    setError("");
    setProgress(0);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 2;
      });
    }, 100);

    try {
      await login(email, password);
      setTimeout(() => {
        setIsLoggingIn(false);
        const stored = localStorage.getItem('username');
        const targetUser = stored || (user && user.username) || 'userid';
        navigate(`/projects/${targetUser}`);
      }, 500);
    } catch (error) {
      setIsLoggingIn(false);
      clearInterval(interval);
      setError(error instanceof Error ? error.message : "Login failed");
    }
  };

  return (
    <div className="pagecontainer">
      <HeaderLogin />
      <div className="mainbody">
        {!isLoggingIn ? (
          <div className="main-content">
            <div className="login-container">
              <div className="login-content">
                <div className="login-form">
                  <h1 className="login-title">Welcome Back</h1>
                  <p className="login-description">
                    Enter your email and password to sign in.
                    Forgotten your password? Click "Forgot password."
                  </p>

                  <label className="login-label">E-mail</label>
                  <input
                    type="email"
                    placeholder="user@example.com"
                    className="login-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />

                  <label className="login-label">Password</label>
                  <input
                    type="password"
                    placeholder="•••••"
                    className="login-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  
                  {error && (
                    <div style={{
                      color: "#ff4444",
                      fontSize: "14px",
                      marginTop: "8px",
                      textAlign: "center"
                    }}>
                      {error}
                    </div>
                  )}
                  
                  <GreenButton className={"login-button"} label="Log in →" onClick={handleLogin} />

                  <div className="divider">
                    <hr className="line" />
                    <span>or</span>
                    <hr className="line" />
                  </div>

                  <button className="static-button">
                    🏛 Log in with your institution
                  </button>

                  <button className="static-button">
                    <img
                      src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                      alt="Google"
                      className="google-icon"
                    />
                    Log in with Google
                  </button>
                </div>
              </div>

              {/* Right: Image */}
              <div className="login-image-container">
                <img
                  src="/images/Login.png"
                  alt="Building"
                  className="login-image"
                />
              </div>
            </div>
          </div>
        ) : (
          <div
            className="main-content"
            style={{
              backgroundColor: "white",
              display: "flex",
              width: "80%",
              height: "90%",
              justifyContent: "center",
              alignItems: "center",
              flexDirection: "column",
            }}
          >
            <div style={{ marginLeft: "120px" }}>
              <ClipLoader size={48} color="#C8F06C" />
            </div>
            <div
              style={{
                marginTop: "30px",
                marginLeft: "120px",
                width: "200px",
                height: "4px",
                backgroundColor: "#eee",
                borderRadius: "2px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progress}%`,
                  backgroundColor: "#C8F06C",
                  transition: "width 0.1s linear",
                }}
              />
            </div>

            <p
              style={{
                color: "#aaa",
                fontSize: "18px",
                marginTop: "12px",
                marginLeft: "120px",
              }}
            >
              {progress} %
            </p>
          </div>
        )}
        <Footer />
      </div>
    </div>
  );
};

export default LoginPage;
