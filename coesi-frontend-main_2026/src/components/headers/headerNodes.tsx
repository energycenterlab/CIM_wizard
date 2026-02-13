import React from "react";
import NodeHeaderMenuButton from "../buttons/nodeHeaderMenuButton";
import LoginButton from "../buttons/loginButton";

const TopMenuBar = () => {
  return (
    <div
      style={{
        height: "4vh",
        display: "flex",
        alignItems: "center",
        padding: "0 100px",
        gap: "100px",
        borderBottom: "1px solid #ddd",
      }}
    >
      {["File", "Edit", "Show", "Models", "Simulation"].map((item) => (
        <NodeHeaderMenuButton key={item} label={item} />
      ))}
    </div>
  );
};

const HeaderBar = () => {
  return (
    <div
      style={{
        height: "10vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 100px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div>
          <img
            src="/urbansim/logo-coesi.png"
            alt="Logo"
            style={{ height: "30px", width: "auto" }}
          />
        </div>

        <input
          defaultValue="Untitled"
          style={{
            fontSize: "18px",
            fontWeight: 800,
            border: "none",
            outline: "none",
            background: "transparent",
          }}
        />
      </div>

      <LoginButton label="Share" onClick={() => {}} />
    </div>
  );
};

const HeaderNodes = () => {
  return (
    <header style={{ width: "100%" }}>
      <TopMenuBar />
      <HeaderBar />
    </header>
  );
};

export default HeaderNodes;
