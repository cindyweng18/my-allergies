import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/") // Flask API endpoint
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setMessage("Failed to connect to backend");
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Allergy Checker</h1>
        <p>{message}</p>
      </header>
    </div>
  );
}

export default App;