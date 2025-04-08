import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Home from "./pages/home";
import Register from "./pages/register";
import AllergyChecker from "./pages/AllergyChecker";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/allergy" element={<AllergyChecker />} />
      </Routes>
    </Router>
  );
}

export default App;