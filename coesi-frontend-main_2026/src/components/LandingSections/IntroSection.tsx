import React, { useState, useEffect, useRef } from "react";

const IntroText = () => {
  return (
    <div
      style={{
        width: "100%",
        backgroundColor: "#F5F2EF",
        borderRadius: "30px",
        padding: "30px",
        display: "flex",
        gap: "72px",
        justifyContent: "space-between",
        alignItems: "center",
        boxSizing: "border-box",
      }}
    >
      <h1
        style={{
          fontSize: "36px",
          fontWeight: "bold",
          lineHeight: "1.5",
          flex: 1,
          maxWidth: "460px",
          textAlign: "left",
        }}
      >
        Coesi is a smart tool that changes based on your real needs
      </h1>
      <p
        style={{
          fontSize: "24px",
          fontWeight: 400,
          lineHeight: "1.6",
          flex: 1,
          textAlign: "left",
        }}
      >
        During the development of Coesi we selected four main stakeholders with
        differents needs and issue. Coesi want to be helpful for all of them by
        providing correct information, and right tool to achieve what you need
      </p>
    </div>
  );
};

interface RoleOption {
  label: string;
  image: string;
  color: string;
}

const roles: RoleOption[] = [
  ["Researcher", "/images/ResearchLine.png", "#C8F06C"],
  ["Citizen", "/images/ResearchLine.png", "#FFD966"],
  ["Public Administration", "/images/ResearchLine.png", "#B5D1FF"],
  ["Energy Provider", "/images/ResearchLine.png", "#FFB3C6"],
].map(([label, image, color]) => ({ label, image, color }));

const CoesiSelectorSection = () => {
  const [selected, setSelected] = useState<RoleOption>(roles[0]);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        open &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open]);

  return (
    <div
      style={{
        width: "100%",
        display: "flex",
        flexDirection: "column",
        gap: "40px",
        paddingRight: "40px",
        paddingBottom: "40px",
        paddingLeft: "0px",
        paddingTop: "0px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "20px",
        }}
      >
        <h1
          style={{
            fontSize: "28px",
            fontWeight: "500",
            margin: 0,
          }}
        >
          Start using COeSI as
        </h1>

        <div ref={dropdownRef} style={{ position: "relative", minWidth: "220px" }}>
          <button
            onClick={() => setOpen(!open)}
            style={{
              backgroundColor: selected.color,
              border: "none",
              borderRadius: "30px",
              padding: "12px 32px",
              fontSize: "28px",
              fontWeight: "500",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              width: "100%",
            }}
          >
            {selected.label} ▼
          </button>

          {open && (
            <div
              style={{
                position: "absolute",
                top: "100%",
                left: 0,
                backgroundColor: "white",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                borderRadius: "12px",
                padding: "16px",
                marginTop: "8px",
                width: "90%", // Match button width
                zIndex: 10,
              }}
            >
              {roles
                .filter((role) => role.label !== selected.label)
                .map((role) => (
                  <div
                    key={role.label}
                    onClick={() => {
                      setSelected(role);
                      setOpen(false);
                    }}
                    style={{
                      padding: "8px 12px",
                      cursor: "pointer",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {role.label}
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
        <img
          src={selected.image}
          alt={selected.label}
          style={{
            maxHeight: "300px",
            objectFit: "contain",
          }}
        />
      </div>
    </div>
  );
};

export default function IntroSection() {
  return (
    <section
      id="intro-section"
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "start",
        flexDirection: "column",
        justifyContent: "center",
        padding: "40px 80px",
        boxSizing: "border-box",
        gap: "80px",
      }}
    >
      <IntroText />
      <CoesiSelectorSection />
    </section>
  );
}
