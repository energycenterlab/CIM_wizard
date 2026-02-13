import React, { useState } from "react";

const NewProjectButtonColourful = ({
  label,
  icon,
  onClick,
  color,
  labelColor,
}: {
  label: string;
  icon: string;
  onClick: () => void;
  color: string;
  labelColor?: string;
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // Function to create a slightly lighter version of the color for hover
  const getHoverColor = (baseColor: string) => {
    // Convert hex to RGB, lighten it, then convert back to hex
    const hex = baseColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Lighten by 15%
    const lightenAmount = 0.15;
    const newR = Math.min(255, Math.round(r + (255 - r) * lightenAmount));
    const newG = Math.min(255, Math.round(g + (255 - g) * lightenAmount));
    const newB = Math.min(255, Math.round(b + (255 - b) * lightenAmount));
    
    return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
  };

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        backgroundColor: isHovered ? getHoverColor(color) : color,
        padding: "24px",
        margin: "24px",
        height: "40px",
        fontSize: "16px",
        color: labelColor || "white",
        fontWeight: 500,
        borderRadius: "999px",
        border: "none",
        cursor: "pointer",
        width: "fit-content",
        transition: "background-color 0.2s ease",
      }}
    >
      <img src={icon} alt="icon" style={{ width: "20px", height: "20px" }} />
      {label}
    </button>
  );
};

export default NewProjectButtonColourful;
