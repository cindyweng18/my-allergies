import React from "react";
import {
  List,
  ListItem,
  TextField,
  Typography,
  IconButton,
  InputAdornment
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";

const AllergyList = ({
  allergies,
  editingAllergy,
  editedValue,
  searchTerm,
  setSearchTerm,
  setEditedValue,
  handleEditAllergy,
  handleSaveEdit,
  handleDeleteAllergy,
}) => {
  const filteredAllergies = allergies.filter((a) =>
    a.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
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
            <ListItem
              key={idx}
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >
              {editingAllergy === a ? (
                <>
                  <TextField
                    value={editedValue}
                    onChange={(e) => setEditedValue(e.target.value)}
                    size="small"
                    sx={{ flexGrow: 1, mr: 1 }}
                    onKeyDown={(e) => e.key === "Enter" && handleSaveEdit()}
                  />
                  <IconButton edge="end" onClick={() => handleDeleteAllergy(a)}>
                    <ClearIcon fontSize="small" />
                  </IconButton>
                </>
              ) : (
                <Typography sx={{ flexGrow: 1 }}>
                  {a.charAt(0).toUpperCase() + a.slice(1)}
                </Typography>
              )}
              <IconButton
                onClick={() =>
                  editingAllergy === a
                    ? handleSaveEdit()
                    : handleEditAllergy(a)
                }
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2" color="text.secondary">
          {searchTerm
            ? "No matching allergies found."
            : "No allergies added yet."}
        </Typography>
      )}
    </>
  );
};

export default AllergyList;
