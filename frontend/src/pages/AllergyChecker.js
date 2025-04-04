import React, { useState, useEffect } from "react";
import axios from "axios";
import { alpha, Box, CssBaseline, Stack, Typography } from "@mui/material";
import AppTheme from "../theme";
import SideMenu from "./SideMenu";
import Navbar from "./Navbar";

const AllergyChecker = (props) => {
  const [allergies, setAllergies] = useState([]);
  const [allergyInput, setAllergyInput] = useState("");
  const [productName, setProductName] = useState("");
  const [productMessage, setProductMessage] = useState("");
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  // Fetch allergies on load
  useEffect(() => {
    const fetchAllergies = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/allergy", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        setAllergies(response.data.allergies || []);
      } catch (error) {
        console.error("Error fetching allergies", error);
      }
    };

    fetchAllergies();
  }, []);

  const handleAddAllergy = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/allergy",
        { allergy: allergyInput },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      setAllergies([...allergies, allergyInput]);
      setAllergyInput("");
    } catch (err) {
      alert(err.response?.data?.message || "Error adding allergy");
    }
  };

  const handleCheckProduct = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/allergy",
        { product_name: productName },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      setProductMessage(response.data.message);
      setProductName("");
    } catch (err) {
      setProductMessage("Error checking product.");
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/allergy/upload",
        formData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setUploadMessage(response.data.message);
      setAllergies([...allergies, ...response.data.allergens]);
    } catch (err) {
      setUploadMessage("Failed to upload file.");
    }
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: 'flex' }}>
        <SideMenu />
        <Navbar />
        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: 'auto',
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: 'center',
              mx: 3,
              pb: 5,
              mt: { xs: 8, md: 0 },
            }}
          >
            <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>

            </Box>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  )
};

export default AllergyChecker;