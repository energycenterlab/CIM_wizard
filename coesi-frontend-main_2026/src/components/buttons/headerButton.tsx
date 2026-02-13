import React, { useState } from "react";

export default function HeaderButton({
  label,
  onClick,
  isActive = false,
}: {
  label: string;
  onClick?: () => void;
  isActive?: boolean;
}) {
  const baseStyle: React.CSSProperties = {
    minWidth: "130px",
    height: "30px",
    padding: "5px 44px",
    borderRadius: "30px",
    backgroundColor: isActive ? "#C8F06C" : "white",
    border: "1px solid rgba(200, 200, 200, 0.2)",
    cursor: "pointer",
    fontFamily: "Host Grotesk, sans-serif",
    fontWeight: 500,
    fontSize: "16px",
    lineHeight: "100%",
    letterSpacing: "0%",
    transition: "background-color 0.2s ease",
  };

  const [isHovered, setIsHovered] = useState(false);

  const getBackgroundColor = () => {
    if (isActive) return "#C8F06C";
    if (isHovered) return "#C8F06C";
    return "white";
  };

  return (
    <button
      style={{
        ...baseStyle,
        backgroundColor: getBackgroundColor(),
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
