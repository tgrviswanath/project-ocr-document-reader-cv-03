import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import DocumentScannerIcon from "@mui/icons-material/DocumentScanner";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <DocumentScannerIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">
          OCR Document Reader
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
