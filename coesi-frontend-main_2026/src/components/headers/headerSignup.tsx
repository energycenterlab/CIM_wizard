import React from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../../main";
import SignupButton from "../buttons/signupButton";
import routes from "../../constants/routes.json";
import { Link } from "react-router-dom";

export default function HeaderSignup() {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);

  return (
    <div
      className="header"
      style={{
        width: "100%",
        height: "10vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 40px",
        backgroundColor: "#fff",
        position: "relative",
        zIndex: 10,
        boxSizing: "border-box",
        borderBottom: "0.5px solid rgba(128, 128, 128, 0.3)",
      }}
    >
      <div style={{
        display: "flex",
        alignItems: "center",
        height: "100%",
      }}>
        <Link to={`${routes.LANDING}`}>
          <img
            src="/urbansim/logo-coesi.png"
            alt="Logo"
            style={{
              height: "80%", // or "36px", just less than 6vh
              width: "auto",
              display: "block",
              margin: 0,
              padding: 0,
              verticalAlign: "middle",
            }}
          />
        </Link>
      </div>

      {!isLoggedIn && (
        <div
          style={{
            display: "flex",
            gap: "30px",
            alignItems: "center",
            fontFamily: "Host Grotesk, sans-serif",
            fontSize: "16px",
            fontWeight: 500,
            height: "100%", // Ensures vertical centering
          }}
        >
          <span>You already have an account?</span>
          <SignupButton label="Login" onClick={() => { window.location.href = routes.LOGIN; }} />
        </div>
      )}
    </div>
  );
}
