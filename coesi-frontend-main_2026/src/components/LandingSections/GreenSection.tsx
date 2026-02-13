export default function GreenSection() {
  return (
    <section
      id="green-section"
      style={{
        width: "100%",
        minHeight: "80vh", 
        display: "flex",
        alignItems: "center",
        flexDirection: "column",
        justifyContent: "center", 
        backgroundColor: "#C8F06C",
      }}
    >
      <h1
        style={{
          fontSize: "48px",
          textAlign: "center",
        }}
      >
        Do you want to study
      </h1>
      <h1
        style={{
          fontSize: "48px",
          textAlign: "center",
        }}
      >
        futures Urban environment?
      </h1>
    </section>
  );
}

/**original <section
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
    </section> */
