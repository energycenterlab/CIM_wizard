import React from "react";

const publications = [
  {
    title:
      "Human–AI collaboration to enable just and inclusive urban energy transition",
    tags: "Ai, Energy justice, Climate Justice, city development",
    date: "June 2025",
  },
  {
    title:
      "Enabling Energy Transitions : A Systematic Case Review of Digital Platforms for Energy Communities",
    tags: "Energy Poverty, Energy Justice, Digital platforms",
    date: "January 2025",
  },
  {
    title: "Digital twin for digital citizen",
    tags: "Social Justice, Energy Justice, Design Justice",
    date: "September 2024",
  },
  {
    title: "Creating Urban digital twin to develop energy safe futures",
    tags: "Ai, Energy justice, Climate Justice, city development",
    date: "March 2024",
  },
  {
    title: "Usign digital platform to foster Enery communites social benefits",
    tags: "Ai, Energy justice, Climate Justice, city development",
    date: "November 2023",
  },
];

const PublicationsTable = () => {
  return (
    <div style={{ width: "100%", padding: "40px" }}>
      <h2
        style={{
          fontSize: "36px",
          fontWeight: "bold",
          marginBottom: "24px",
          textAlign: "left",
        }}
      >
        Last publication about{" "}
        <span style={{ fontFamily: "monospace" }}>Coesi</span>
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 2fr 1fr",
          padding: "16px 0",
          fontWeight: "500",
          color: "#444",
          borderBottom: "1px solid #ccc",
        }}
      >
        <div style={{ textAlign: "left" }}>Title</div>
        <div style={{ textAlign: "left" }}>Tags</div>
        <div style={{ textAlign: "left" }}>Date</div>
      </div>

      {publications.map((pub, idx) => (
        <div
          key={idx}
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 2fr 1fr",
            padding: "16px 0",
            borderBottom: "1px solid #ddd",
            alignItems: "start",
            textAlign: "left",
          }}
        >
          <div style={{ fontStyle: "italic", fontWeight: "500" }}>
            {pub.title}
          </div>
          <div style={{ color: "#555" }}>{pub.tags}</div>
          <div style={{ color: "#888", whiteSpace: "nowrap" }}>{pub.date}</div>
        </div>
      ))}
    </div>
  );
};

export default function PublicationSection() {
  return (
    <section
      id="publications-section"
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
      <PublicationsTable />
    </section>
  );
}
