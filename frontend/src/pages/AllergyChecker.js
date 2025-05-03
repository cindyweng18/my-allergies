import React, { useState, useEffect } from "react";
import axios from "axios";
import { Alert, Box, Button, CssBaseline, Grid, List, ListItem, Paper, Snackbar, TextField, Typography } from "@mui/material";
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
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  // Fetch allergies on load
  useEffect(() => {
    const fetchAllergies = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/allergy/", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          withCredentials: true,
        });
        setAllergies(response.data.allergies || []);
      } catch (error) {
        console.error("Error fetching allergies", error);
        navigate('/')
      }
    };

    fetchAllergies();
  }, []);

  const showSnackbar = (message, severity = "success") => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleAddAllergy = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/allergy/add",
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
      showSnackbar("Allergy added successfully!");
    } catch (err) {
      alert(err.response?.data?.message || "Error adding allergy");
    }
  };

  const handleCheckProduct = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/allergy/check_product",
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
      showSnackbar(response.data.message);
      setUploadMessage(response.data.message);
      setAllergies([...allergies, ...response.data.allergens]);
    } catch (err) {
      setUploadMessage("Failed to upload file.");
    }
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
        <Box sx={{ display: "flex" }}>
        <SideMenu />
        <Navbar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 4,
            backgroundColor: (theme) =>
              theme.palette.mode === "light" ? "#f5f5f5" : "#121212",
          }}
        >
          <Typography variant="h4" gutterBottom>
            Allergy Checker
          </Typography>

          <Grid container spacing={3}>
            {/* Add Allergy */}
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Add an Allergy
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Write down your allergies here to track them and check for reactions later.
                </Typography>
                <form onSubmit={handleAddAllergy}>
                  <TextField
                    label="Enter an allergy"
                    value={allergyInput}
                    onChange={(e) => setAllergyInput(e.target.value)}
                    fullWidth
                    required
                    sx={{ mb: 2 }}
                  />
                  <Button fullWidth variant="contained" type="submit">
                    Add Allergy
                  </Button>
                </form>
              </Paper>
            </Grid>

            {/* Upload File */}
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Upload a File
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Upload a file such as an image or PDF of ingredients. Allergens will be extracted automatically.
                </Typography>
                <form onSubmit={handleFileUpload}>
                  <Button variant="outlined" component="label" fullWidth sx={{ mb: 2 }}>
                    Choose File
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      hidden
                      onChange={(e) => setFile(e.target.files[0])}
                    />
                  </Button>
                  <Button fullWidth variant="contained" type="submit">
                    Upload and Scan
                  </Button>
                </form>
                {uploadMessage && (
                  <Typography variant="body2" color="text.secondary" mt={2}>
                    {uploadMessage}
                  </Typography>
                )}
              </Paper>
            </Grid>

            {/* Check Product */}
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Check Product for Allergens
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Enter the name of a product or meal to see if it contains any of your listed allergies.
                </Typography>
                <form onSubmit={handleCheckProduct}>
                  <TextField
                    label="Enter product name"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    fullWidth
                    required
                    sx={{ mb: 2 }}
                  />
                  <Button fullWidth variant="contained" type="submit">
                    Check Product
                  </Button>
                </form>
                {productMessage && (
                  <Typography variant="body2" color="text.secondary" mt={2}>
                    {productMessage}
                  </Typography>
                )}
              </Paper>
            </Grid>

            {/* Allergy List */}
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Your Allergies
                </Typography>
                {allergies.length > 0 ? (
                  <List dense>
                    {allergies.map((a, idx) => (
                      <ListItem key={idx} sx={{ listStyleType: 'disc', display: 'list-item' }}>
                        {a.charAt(0).toUpperCase() + a.slice(1)}
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No allergies added yet! Start with adding some or upload a file.
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Box>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </AppTheme>
  )
};

export default AllergyChecker;