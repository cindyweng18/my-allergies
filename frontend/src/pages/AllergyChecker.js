import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
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
  InputAdornment
} from "@mui/material";
import EditIcon from '@mui/icons-material/Edit';
import ClearIcon from '@mui/icons-material/Clear';
import AppTheme from "../theme";
import SideMenu from "./SideMenu";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";
import SelectAllergens from "./SelectAllergies";

const AllergyChecker = (props) => {
  const navigate = useNavigate();
  const [allergies, setAllergies] = useState([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");
  const [searchTerm, setSearchTerm] = useState("");
  const [editingAllergy, setEditingAllergy] = useState(null);
  const [editedValue, setEditedValue] = useState("");
  const [uploadAllergens, setUploadAllergens] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [newAllergy, setNewAllergy] = useState("");
  const [file, setFile] = useState(null);
  const [productName, setProductName] = useState("");
  const [productCheckResult, setProductCheckResult] = useState("");
  const [checkingProduct, setCheckingProduct] = useState(false);
  const [productVerdict, setProductVerdict] = useState(null);
  const [productExplanation, setProductExplanation] = useState("");
  const [showExplanation, setShowExplanation] = useState(false);


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

  const handleEditAllergy = (name) => {
    setEditingAllergy(name);
    setEditedValue(name);
  };

  const handleSaveEdit = async () => {
    if (!editedValue.trim()) return;
    try {
      await axios.put("http://127.0.0.1:5000/allergy/edit", {
        old_name: editingAllergy,
        new_name: editedValue.trim().toLowerCase(),
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      setAllergies((prev) =>
        prev.map((a) => (a === editingAllergy ? editedValue.trim().toLowerCase() : a))
      );
      setEditingAllergy(null);
      setEditedValue("");
      showSnackbar("Allergy updated successfully");
    } catch {
      showSnackbar("Failed to update allergy", "error");
    }
  };

  const handleAddAllergy = async () => {
    const trimmed = newAllergy.trim().toLowerCase();
    if (!trimmed) return;

    if (allergies.includes(trimmed)) {
      showSnackbar("Allergy already exists", "warning");
      return;
    }

    try {
      await axios.post("http://127.0.0.1:5000/allergy/add", {
        allergy: trimmed,
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });

      setAllergies((prev) => [...prev, trimmed]);
      setNewAllergy("");
      showSnackbar("Allergy added!");
    } catch {
      showSnackbar("Failed to add allergy", "error");
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

      setUploadAllergens(response.data.allergens);
      setModalOpen(true);
    } catch {
      showSnackbar("Failed to upload file.", "error");
    }
  };

  const handleConfirmAllergens = async (selectedAllergens) => {
    try {
      await axios.post("http://127.0.0.1:5000/allergy/add_batch", {
        allergies: selectedAllergens
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      setAllergies((prev) => [...prev, ...selectedAllergens]);
      showSnackbar("Selected allergies added!");
    } catch {
      showSnackbar("Error saving selected allergens.", "error");
    } finally {
      setModalOpen(false);
      setUploadAllergens([]);
    }
  };

  const filteredAllergies = allergies.filter((a) =>
    a.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCheckProduct = async () => {
    if (!productName.trim()) return;

    setCheckingProduct(true);
    setProductVerdict(null);
    setProductExplanation("");
    setShowExplanation(false);

    try {
      const response = await axios.post("http://127.0.0.1:5000/allergy/check_product", {
        product_name: productName
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });

      setProductVerdict(response.data.verdict);
      setProductExplanation(response.data.explanation);
    } catch {
      showSnackbar("Failed to check product", "error");
    } finally {
      setCheckingProduct(false);
    }
  };


  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: "flex" }}>
        <SideMenu />
        <Navbar />
        <Box component="main" sx={{ flexGrow: 1, p: 4 }}>
          <Typography variant="h4" gutterBottom>Allergy Checker</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6">Add an Allergy</Typography>
                <TextField
                  label="Add a new allergy"
                  variant="outlined"
                  size="small"
                  fullWidth
                  sx={{ my: 1 }}
                  value={newAllergy}
                  onChange={(e) => setNewAllergy(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddAllergy()}
                />
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleAddAllergy}
                  disabled={!newAllergy.trim()}
                  sx={{ mb: 2 }}
                >
                  Add Allergy
                </Button>
                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle1" sx={{ mb: 1 }}>Upload Allergy Report</Typography>
                <Button
                  variant="outlined"
                  component="label"
                  size="small"
                >
                  Choose File
                  <input
                    type="file"
                    hidden
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files[0])}
                  />
                </Button>

                <Button
                  variant="contained"
                  color="primary"
                  size="small"
                  onClick={handleFileUpload}
                  disabled={!file}
                  sx={{ ml: 2 }}
                >
                  Upload
                </Button>
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
                {filteredAllergies.length > 0 ? (
                  <List dense>
                    {filteredAllergies.map((a, idx) => (
                      <ListItem key={idx} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        {editingAllergy === a ? (
                          <TextField
                            value={editedValue}
                            onChange={(e) => setEditedValue(e.target.value)}
                            size="small"
                            sx={{ flexGrow: 1, mr: 1 }}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit()}
                          />
                        ) : (
                          <Typography sx={{ flexGrow: 1 }}>{a.charAt(0).toUpperCase() + a.slice(1)}</Typography>
                        )}
                        <IconButton onClick={() => editingAllergy === a ? handleSaveEdit() : handleEditAllergy(a)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm ? "No matching allergies found." : "No allergies added yet."}
                  </Typography>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6">Check Product Safety</Typography>
              <TextField
                label="Enter product name"
                variant="outlined"
                size="small"
                fullWidth
                sx={{ my: 2 }}
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
              />
              <Button
                variant="contained"
                onClick={handleCheckProduct}
                disabled={!productName || checkingProduct}
              >
                {checkingProduct ? <CircularProgress size={20} color="inherit" /> : "Check"}
              </Button>

              {productVerdict && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Verdict: {productVerdict}</Typography>

                {productExplanation && (
                  <>
                    <Button
                      size="small"
                      variant="text"
                      sx={{ mt: 1 }}
                      onClick={() => setShowExplanation(prev => !prev)}
                    >
                      {showExplanation ? "Hide Explanation" : "Show Explanation"}
                    </Button>

                    {showExplanation && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {productExplanation}
                      </Typography>
                    )}
                  </>
                )}
              </Box>
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

      <SelectAllergens
        open={modalOpen}
        allergens={uploadAllergens}
        onClose={() => setModalOpen(false)}
        onConfirm={handleConfirmAllergens}
      />
    </AppTheme>
  );
};

export default AllergyChecker;