import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Alert,
  Box,
  Button,
  CssBaseline,
  Grid,
  List,
  ListItem,
  Paper,
  Snackbar,
  TextField,
  Typography,
  Divider,
  Checkbox,
  IconButton,
} from "@mui/material";
import InputAdornment from "@mui/material/InputAdornment";
import ClearIcon from '@mui/icons-material/Clear';
import AppTheme from "../theme";
import SideMenu from "./SideMenu";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

const AllergyChecker = (props) => {
  const navigate = useNavigate();
  const [allergies, setAllergies] = useState([]);
  const [newAllergens, setNewAllergens] = useState([]);
  const [allergyInput, setAllergyInput] = useState("");
  const [productName, setProductName] = useState("");
  const [productMessage, setProductMessage] = useState("");
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");
  const [selectedAllergies, setSelectedAllergies] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchAllergies = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/allergy/", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        setAllergies(response.data.allergies || []);
      } catch (error) {
        console.error("Error fetching allergies", error);
        navigate("/");
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
    const cleaned = allergyInput.trim().toLowerCase();
    if (!cleaned || !/^[a-zA-Z\s\-]+$/.test(cleaned)) {
      showSnackbar("Invalid allergy name.", "error");
      return;
    }
    try {
      await axios.post("http://127.0.0.1:5000/allergy/add", { allergy: cleaned }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      setAllergies((prev) => [...prev, cleaned]);
      setNewAllergens([cleaned]);
      setTimeout(() => setNewAllergens([]), 3000);
      setAllergyInput("");
      showSnackbar("Allergy added successfully!");
    } catch (err) {
      showSnackbar("Error adding allergy.", "error");
    }
  };

  const handleCheckProduct = async (e) => {
    e.preventDefault();
    const cleaned = productName.trim().toLowerCase();
    if (!cleaned || cleaned.length < 2) {
      showSnackbar("Invalid product name.", "error");
      return;
    }
    try {
      const response = await axios.post("http://127.0.0.1:5000/allergy/check_product", { product_name: cleaned }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      setProductMessage(response.data.message);
      setProductName("");
    } catch {
      showSnackbar("Failed to check product.", "error");
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post("http://127.0.0.1:5000/allergy/upload", formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setAllergies((prev) => [...prev, ...response.data.allergens]);
      setUploadMessage(response.data.message);
      showSnackbar(response.data.message);
    } catch {
      showSnackbar("Failed to upload file.", "error");
    }
  };

  const toggleSelectAllergy = (name) => {
    setSelectedAllergies((prev) =>
      prev.includes(name) ? prev.filter((a) => a !== name) : [...prev, name]
    );
  };

  const handleBatchDelete = async () => {
    if (selectedAllergies.length === 0) return;
    if (!window.confirm("Delete selected allergies?")) return;
    try {
      await axios.post("http://127.0.0.1:5000/allergy/delete_batch", { allergies: selectedAllergies }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      setAllergies((prev) => prev.filter((a) => !selectedAllergies.includes(a)));
      setSelectedAllergies([]);
      showSnackbar("Selected allergies deleted.");
    } catch {
      showSnackbar("Failed to delete allergies.", "error");
    }
  };

  const filteredAllergies = allergies.filter((a) =>
    a.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: "flex" }}>
        <SideMenu />
        <Navbar />
        <Box component="main" sx={{ flexGrow: 1, p: 4 }}>
          <Typography variant="h4" gutterBottom>Allergy Checker</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6">Add an Allergy</Typography>
                <form onSubmit={handleAddAllergy}>
                  <TextField label="Enter an allergy" value={allergyInput} onChange={(e) => setAllergyInput(e.target.value)} fullWidth required sx={{ mt: 2, mb: 2 }} />
                  <Button fullWidth variant="contained" type="submit">Add Allergy</Button>
                </form>
              </Paper>

              <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6">Upload a File</Typography>
                <form onSubmit={handleFileUpload}>
                  <Button variant="outlined" component="label" fullWidth sx={{ mt: 2, mb: 2 }}>
                    Choose File
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png" hidden onChange={(e) => setFile(e.target.files[0])} />
                  </Button>
                  <Button fullWidth variant="contained" type="submit">Upload and Scan</Button>
                </form>
              </Paper>

              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6">Check Product for Allergens</Typography>
                <form onSubmit={handleCheckProduct}>
                  <TextField label="Enter product name" value={productName} onChange={(e) => setProductName(e.target.value)} fullWidth required sx={{ mt: 2, mb: 2 }} />
                  <Button fullWidth variant="contained" type="submit">Check Product</Button>
                </form>
                {productMessage && <Typography sx={{ mt: 2 }}>{productMessage}</Typography>}
              </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6">Your Allergies</Typography>
                <TextField
                  label="Search allergies"
                  variant="outlined"
                  size="small"
                  fullWidth
                  sx={{ my: 2 }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    endAdornment: searchTerm && (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setSearchTerm("")} edge="end">
                          <ClearIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />
                <TextField
                  label="Search allergies"
                  variant="outlined"
                  size="small"
                  fullWidth
                  sx={{ my: 2 }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {filteredAllergies.length > 0 ? (
                  <>
                    <List dense>
                      {filteredAllergies.map((a, idx) => {
                        const isNew = newAllergens.includes(a);
                        const isSelected = selectedAllergies.includes(a);
                        return (
                          <ListItem
                            key={idx}
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              bgcolor: isNew ? 'rgba(100, 221, 23, 0.2)' : 'inherit',
                              borderRadius: 1,
                              transition: 'background-color 0.3s ease-in-out',
                            }}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                              <Checkbox checked={isSelected} onChange={() => toggleSelectAllergy(a)} />
                              <Typography>{a.charAt(0).toUpperCase() + a.slice(1)}</Typography>
                            </Box>
                          </ListItem>
                        );
                      })}
                    </List>
                    {selectedAllergies.length > 0 && (
                      <Button variant="outlined" color="error" fullWidth sx={{ mt: 2 }} onClick={handleBatchDelete}>
                        Delete Selected ({selectedAllergies.length})
                      </Button>
                    )}
                  </>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm ? "No matching allergies found." : "No allergies added yet. Start by adding or uploading."}
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Box>
      <Snackbar open={snackbarOpen} autoHideDuration={4000} onClose={() => setSnackbarOpen(false)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={() => setSnackbarOpen(false)} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </AppTheme>
  );
};

export default AllergyChecker;