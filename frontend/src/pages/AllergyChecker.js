import React, { useState, useEffect } from "react";
import axios from "axios";
import { alpha, Box, Button, CssBaseline, List, ListItem, Paper, Stack, TextField, Typography } from "@mui/material";
import AppTheme from "../theme";
import SideMenu from "./SideMenu";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

const AllergyChecker = (props) => {
  const navigate = useNavigate();
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
        navigate('/')
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
            <Box p={4} maxWidth={600} mx="auto">
      <Typography variant="h4" gutterBottom>
        Allergy Checker
      </Typography>
        <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
          <form onSubmit={handleAddAllergy}>
            <TextField
              label="Enter an allergy"
              value={allergyInput}
              onChange={(e) => setAllergyInput(e.target.value)}
              fullWidth
              required
              sx={{ mb: 2 }}
            />
            <Button variant="contained" type="submit">
              Add Allergy
            </Button>
          </form>
        </Paper>

        <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
          <form onSubmit={handleFileUpload}>
            <Button
              variant="outlined"
              component="label"
              sx={{ mb: 2 }}
            >
              Upload File
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                hidden
                onChange={(e) => setFile(e.target.files[0])}
              />
            </Button>
            <Button variant="contained" type="submit" sx={{ ml: 2 }}>
              Upload and Scan
            </Button>
          </form>
          <Typography variant="body2" color="text.secondary" mt={1}>
            {uploadMessage}
          </Typography>
        </Paper>

        <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
          <form onSubmit={handleCheckProduct}>
            <TextField
              label="Check a product"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              fullWidth
              required
              sx={{ mb: 2 }}
            />
            <Button variant="contained" type="submit">
              Check
            </Button>
          </form>
          <Typography variant="body2" color="text.secondary" mt={1}>
            {productMessage}
          </Typography>
        </Paper>

        <Typography variant="h6" gutterBottom>
          Your Allergies:
        </Typography>
        <List>
          {allergies.map((a, idx) => (
            <ListItem key={idx}>{a}</ListItem>
          ))}
        </List>
      </Box>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  )
};

export default AllergyChecker;