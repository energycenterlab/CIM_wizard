import React, { useState } from "react";

export default function LoginButton({
  label,
  onClick,
}: {
  label: string;
  onClick?: () => void;
}) {
  const [isHovered, setIsHovered] = useState(false);

  const baseStyle: React.CSSProperties = {
    width: "180px",
    height: "32px",
    minWidth: "180px",
    padding: "5px 44px",
    gap: "10px",
    borderRadius: "30px",
    backgroundColor: isHovered ? "#fff" : "#000",
    color: isHovered ? "#000" : "#fff",
    border: isHovered ? "1px solid black" : "none",
    cursor: "pointer",
    fontFamily: "Host Grotesk, sans-serif",
    fontWeight: 500,
    fontSize: "16px",
    lineHeight: "100%",
    transition: "all 0.2s ease",
  };

  return (
    <button
      style={baseStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
