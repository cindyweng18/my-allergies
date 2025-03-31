import React from "react";
import { Link } from "react-router-dom";
import "../App.css"

function Home() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Allergy Checker</h1>
        <Link to="/login">Go to Login</Link>
      </header>
    </div>
  );
}

export default Home;
