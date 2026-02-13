const Legend = () => {
  return(
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      marginTop: "20px",
      padding: "10px",
      background: "#f0f0f0",
      borderTop: "2px solid black",
      borderRadius: "5px",
    }}>
    
      <div style={{ display: "flex", alignItems: "center", marginRight: "20px" }}>
        <div style={{
          width: "12px",
          height: "12px",
          backgroundColor: "green",
          borderRadius: "50%",
          border: "2px solid white",
          marginRight: "5px"
        }} />
        <span>Input</span>
      </div>

      <div style={{ display: "flex", alignItems: "center" }}>
        <div style={{
          width: "12px",
          height: "12px",
          backgroundColor: "red",
          borderRadius: "50%",
          border: "2px solid white",
          marginRight: "5px"
        }} />
        <span>Output</span>
      </div>
    </div>
  )
}

export default Legend