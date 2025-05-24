import React from "react";
import { Box, CssBaseline, Typography, Paper } from "@mui/material";
import AppTheme from "../theme";
import SideMenu from "../components/SideMenu";
import Navbar from "../components/Navbar";

export default function AboutPage(props) {
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
            minHeight: "100vh",
          }}
        >
          <Typography variant="h4" gutterBottom>
            About This App
          </Typography>
          <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
            <Typography variant="body1" gutterBottom>
              The Allergy Checker is a health-focused application designed to help users track their allergies, scan ingredients from products, and verify safety using AI analysis.
            </Typography>
            <Typography variant="body1" gutterBottom>
              Upload files or images, input allergy data manually, and receive real-time feedback powered by Gemini AI. Our goal is to empower you with reliable allergy management tools.
            </Typography>
            <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
              Created by Cindy B • Built with Flask, React, Material UI, and love ♥
            </Typography>
          </Paper>
        </Box>
      </Box>
    </AppTheme>
  );
}