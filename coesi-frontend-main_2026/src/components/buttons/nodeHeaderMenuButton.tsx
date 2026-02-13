import React from "react";

const NodeHeaderMenuButton = ({ label }: { label: string }) => {
  return (
    <button
      onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#f2f2f2")}
      onMouseOut={(e) =>
        (e.currentTarget.style.backgroundColor = "transparent")
      }
      style={{
        background: "none",
        border: "none",
        padding: "4px 8px",
        borderRadius: "10px",
        cursor: "pointer",
        fontSize: "14px",
        color: "#444",
      }}
    >
      {label}
    </button>
  );
};

export default NodeHeaderMenuButton;
