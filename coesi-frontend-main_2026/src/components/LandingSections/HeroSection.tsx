import { useNavigate } from "react-router-dom";
import React from "react";

import routes from "../../constants/routes.json";

import GreenButton from "../buttons/greenButton";
import { log } from "console";

export default function HeroSection() {
  const navigate = useNavigate();
  const login = () => {
    navigate(`${routes.PROJECTSDEMO}`);
  };
  return (
    <section
      id="hero-section"
      style={{
        width: "100%",
        minHeight: "80vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 80px",
        boxSizing: "border-box",
        gap: "80px",
      }}
    >
      <div
        style={{
          maxWidth: "500px",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <h1
          style={{
            fontSize: "36px",
            fontWeight: "bold",
            lineHeight: "1.5",
            marginBottom: "16px",
            maxWidth: "100%",
            textAlign: "left",
          }}
        >
          Design energy efficient cities by using COESI
        </h1>
        <p
          style={{
            fontSize: "24px",
            lineHeight: "1.5",
            marginBottom: "24px",
            maxWidth: "100%",
            textAlign: "left",
          }}
        >
          Design energy efficient cities by using COESI, a node based tool to
          create custom energy model.
        </p>
        <GreenButton label="Try COeSI →" onClick={login} />
      </div>

      <div>
        <img
          src="/images/LandingHero.png"
          alt="COESI preview"
          style={{
            maxWidth: "600px",
            width: "100%",
            height: "auto",
            borderRadius: "20px",
          }}
        />
      </div>
    </section>
  );
}
