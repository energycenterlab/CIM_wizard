import React from "react";

type GreenButtonProps = {
  label: string;
  onClick?: () => void;
  className?: string;
  style?: React.CSSProperties;
};

export default function GreenButton({
  label,
  onClick,
  className = "",
  style,
}: GreenButtonProps) {
  const defaultStyle: React.CSSProperties = {
    backgroundColor: "#C8F06C",
    border: "none",
    borderRadius: "30px",
    padding: "10px 32px",
    fontSize: "20px",
    fontWeight: 500,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    fontFamily: "Host Grotesk, sans-serif",
    width: "100%",
    boxSizing: "border-box",
  };

  // Combine provided className with default
  const combinedClassName = ["green-button", className]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      className={combinedClassName}
      style={{ ...defaultStyle, ...style }}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
