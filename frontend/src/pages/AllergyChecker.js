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
  InputAdornment
} from "@mui/material";
import EditIcon from '@mui/icons-material/Edit';
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
  const [editingAllergy, setEditingAllergy] = useState(null);
  const [editedValue, setEditedValue] = useState("");

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