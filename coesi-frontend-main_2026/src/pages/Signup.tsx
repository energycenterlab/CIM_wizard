import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import routes from "../constants/routes.json";
import HeaderSignup from "../components/headers/headerSignup";
import Footer from "../components/Footer";

import GreenButton from "../components/buttons/greenButton";
import { useAuth } from "../contexts/AuthContext";
import "./login.css";

const EyeIcon = ({ open }: { open: boolean }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ verticalAlign: "middle" }}
  >
    {open ? (
      <path d="M1 12C1 12 5 5 12 5C19 5 23 12 23 12C23 12 19 19 12 19C5 19 1 12 1 12Z" stroke="#888" strokeWidth="2" fill="none"/>
      ) : (
      <>
        <path d="M1 12C1 12 5 5 12 5C19 5 23 12 23 12C23 12 19 19 12 19C5 19 1 12 1 12Z" stroke="#888" strokeWidth="2" fill="none"/>
        <line x1="3" y1="21" x2="21" y2="3" stroke="#888" strokeWidth="2"/>
      </>
    )}
    <circle cx="12" cy="12" r="3.5" stroke="#888" strokeWidth="2" fill="none"/>
  </svg>
);

type RoleOption = {
  label: string;
  color: string;
};

const roles: RoleOption[] = [
  { label: "Researcher", color: "#C8F06C" },
  { label: "Citizen", color: "#FFD966" },
  { label: "Public Administration", color: "#B5D1FF" },
  { label: "Energy Provider", color: "#FFB3C6" },
];

const ErrorTooltip = ({ message, isVisible }: { message: string; isVisible: boolean }) => {
  if (!isVisible) return null;
  
  return (
    <div
      style={{
        position: "absolute",
        top: "calc(100% - 2px)",
        left: "0",
        backgroundColor: "#f8f9fa",
        border: "1px solid #dee2e6",
        borderRadius: "8px",
        padding: "8px 12px",
        fontSize: "12px",
        color: "#d32f2f",
        zIndex: 1000,
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
        maxWidth: "300px",
        display: "flex",
        alignItems: "center",
        gap: "8px"
      }}
    >
      {/* Arrow pointing up to input */}
      <div
        style={{
          position: "absolute",
          top: "-6px",
          left: "20px",
          width: "0",
          height: "0",
          borderLeft: "6px solid transparent",
          borderRight: "6px solid transparent",
          borderBottom: "6px solid #f8f9fa"
        }}
      />
      {/* Arrow border */}
      <div
        style={{
          position: "absolute",
          top: "-7px",
          left: "20px",
          width: "0",
          height: "0",
          borderLeft: "6px solid transparent",
          borderRight: "6px solid transparent",
          borderBottom: "6px solid #dee2e6"
        }}
      />
      <div
        style={{
          width: "16px",
          height: "16px",
          backgroundColor: "#ff9800",
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0
        }}
      >
        <span style={{ color: "white", fontSize: "10px", fontWeight: "bold" }}>!</span>
      </div>
      <span>{message}</span>
    </div>
  );
};

const SignupPage = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [selectedRole, setSelectedRole] = useState<RoleOption>(roles[0]);
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [errors, setErrors] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });

  const navigate = useNavigate();
  const { register } = useAuth();
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        roleDropdownOpen &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setRoleDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [roleDropdownOpen]);

  const validateForm = () => {
    const newErrors = {
      username: "",
      email: "",
      password: "",
      confirmPassword: ""
    };

    if (!username.trim()) {
      newErrors.username = "Username is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== "");
  };

  const handleRegister = async () => {
    if (validateForm()) {
      try {
        await register(username, email, password, selectedRole.label);
        setRegistrationSuccess(true);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Registration failed";
        setError(errorMessage);
      }
    }
  };

  if (registrationSuccess) {
    return (
      <div className="pagecontainer">
        <HeaderSignup />
        <div className="mainbody">
          <div className="main-content">
            <div className="login-container">
              <div className="login-content" style={{ 
                alignItems: "center",
                justifyContent: "center",
                minHeight: "80vh"
              }}>
                <div className="login-form" style={{ 
                  justifyContent: "center", 
                  alignItems: "center", 
                  textAlign: "center",
                  display: "flex",
                  flexDirection: "column",
                  height: "100%"
                }}>
                  <h1 className="login-title" style={{ whiteSpace: "nowrap" }}>Registration Successful!</h1>
                  <p className="login-description">
                    Registration was successful. Please confirm your email.
                  </p>
                  <GreenButton 
                    className={"login-button"} 
                    label="Back to Login" 
                    onClick={() => navigate(routes.LOGIN)} 
                  />
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
          <Footer />
        </div>
      </div>
    );
  }

  return (
    <div className="pagecontainer">
      <HeaderSignup />
      <div className="mainbody">
        <div className="main-content">
          <div className="login-container">
            <div className="login-content">
              <div className="login-form" style={{ paddingTop: "20px" }}>
                <h1 className="login-title">Sign Up</h1>
                <p className="login-description">
                  Create your account to get started.
                </p>

                <label className="login-label">Username</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    placeholder="Your username"
                    className="login-input"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={{
                      border: errors.username ? "1px solid #d32f2f" : "1px solid #ccc"
                    }}
                  />
                  <ErrorTooltip message={errors.username} isVisible={errors.username !== ""} />
                </div>

                <label className="login-label">E-mail</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="email"
                    placeholder="user@example.com"
                    className="login-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                      border: errors.email ? "1px solid #d32f2f" : "1px solid #ccc"
                    }}
                  />
                  <ErrorTooltip message={errors.email} isVisible={errors.email !== ""} />
                </div>

                <label className="login-label">Password</label>
                <div style={{ position: "relative" }}>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="•••••"
                    className="login-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                      paddingRight: 40,
                      border: errors.password ? "1px solid #d32f2f" : "1px solid #ccc"
                    }}
                  />
                  <button
                    type="button"
                    style={{
                      position: "absolute",
                      right: 20,
                      top: "45%",
                      transform: "translateY(-50%)",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      padding: 0,
                      margin: 0,
                      height: "24px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "24px",
                      lineHeight: 0
                    }}
                    onClick={() => setShowPassword((v) => !v)}
                    tabIndex={-1}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <EyeIcon open={showPassword} />
                  </button>
                  <ErrorTooltip message={errors.password} isVisible={errors.password !== ""} />
                </div>

                <label className="login-label">Confirm Password</label>
                <div style={{ position: "relative" }}>
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="•••••"
                    className="login-input"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{
                      paddingRight: 40,
                      border: errors.confirmPassword ? "1px solid #d32f2f" : "1px solid #ccc"
                    }}
                  />
                  <button
                    type="button"
                    style={{
                      position: "absolute",
                      right: 20,
                      top: "45%",
                      transform: "translateY(-50%)",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      padding: 0,
                      margin: 0,
                      height: "24px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "24px",
                      lineHeight: 0
                    }}
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    tabIndex={-1}
                    aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                  >
                    <EyeIcon open={showConfirmPassword} />
                  </button>
                  <ErrorTooltip message={errors.confirmPassword} isVisible={errors.confirmPassword !== ""} />
                </div>

                <label className="login-label">Start using COeSI as</label>
                <div style={{ position: "relative" }} ref={dropdownRef}>
                  <button
                    type="button"
                    onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                    className="login-input"
                    style={{
                      backgroundColor: selectedRole.color,
                      position: "relative"
                    }}
                  >
                    {selectedRole.label} ▼
                    
                    {roleDropdownOpen && (
                      <div
                        style={{
                          position: "absolute",
                          top: "100%",
                          left: 0,
                          backgroundColor: "white",
                          border: "1px solid #ccc",
                          borderRadius: "12px",
                          padding: "8px 0",
                          marginTop: "4px",
                          width: "100%",
                          zIndex: 10,
                          boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                        }}
                      >
                        {roles
                          .filter((role) => role.label !== selectedRole.label)
                          .map((role) => (
                            <div
                              key={role.label}
                              onClick={() => {
                                setSelectedRole(role);
                                setRoleDropdownOpen(false);
                              }}
                              style={{
                                padding: "8px 20px",
                                cursor: "pointer",
                                fontSize: "14px",
                                color: "#333",
                                backgroundColor: "white",
                                borderRadius: "8px",
                                margin: "2px 0"
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = "#f5f5f5";
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = "white";
                              }}
                            >
                              {role.label}
                            </div>
                          ))}
                      </div>
                    )}
                  </button>
                </div>

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
                
                <GreenButton className={"login-button"} label="Register" onClick={handleRegister} />
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
        <Footer />
      </div>
    </div>
  );
};

export default SignupPage;
