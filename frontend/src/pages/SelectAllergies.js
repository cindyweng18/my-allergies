import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
} from "@mui/material";

export default function SelectAllergens({ open, allergens, onClose, onConfirm }) {
  const [selected, setSelected] = React.useState([]);

  const toggleAllergen = (name) => {
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((a) => a !== name) : [...prev, name]
    );
  };

  React.useEffect(() => {
    setSelected([]);
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Select Allergens</DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Select only the allergens you are positively allergic to:
        </Typography>
        <FormGroup>
          {allergens.map((a, i) => (
            <FormControlLabel
              key={i}
              control={
                <Checkbox
                  checked={selected.includes(a)}
                  onChange={() => toggleAllergen(a)}
                />
              }
              label={a.charAt(0).toUpperCase() + a.slice(1)}
            />
          ))}
        </FormGroup>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={() => onConfirm(selected)} variant="contained">
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
}