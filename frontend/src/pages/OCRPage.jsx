import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Divider, IconButton, Tooltip, Tabs, Tab,
  TextField, LinearProgress,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckIcon from "@mui/icons-material/Check";
import { extractText } from "../services/ocrApi";

export default function OCRPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState(0);
  const [copied, setCopied] = useState(false);
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    setTab(0);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await extractText(fd);
      setResult({ ...r.data, filename: file.name });
    } catch (e) {
      setError(e.response?.data?.detail || "OCR extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result?.text || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentText = result
    ? (tab === 0 ? result.text : result.page_texts?.[tab - 1] || "")
    : "";

  return (
    <Box>
      {/* Drop zone */}
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{
          p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed",
          "&:hover": { bgcolor: "action.hover" },
        }}
      >
        <input ref={fileRef} type="file" hidden
          accept=".jpg,.jpeg,.png,.bmp,.webp,.pdf"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box>
              <CircularProgress size={28} sx={{ mb: 1 }} />
              <Typography color="text.secondary">Extracting text…</Typography>
            </Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Box>
                <Typography color="text.secondary">
                  Drag & drop or click to upload
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  JPG · PNG · BMP · WEBP · PDF
                </Typography>
              </Box>
            </Box>
        }
      </Paper>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          {/* Stats */}
          <Box sx={{ display: "flex", gap: 1.5, mb: 2, flexWrap: "wrap", alignItems: "center" }}>
            <Chip label={`📄 ${result.filename}`} variant="outlined" size="small" />
            <Chip label={`${result.pages} page${result.pages !== 1 ? "s" : ""}`} size="small" />
            <Chip label={`${result.word_count} words`} color="primary" size="small" />
            <Chip label={`${result.words?.length || 0} tokens detected`} variant="outlined" size="small" />
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Page tabs (only for multi-page PDFs) */}
          {result.pages > 1 && (
            <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }} variant="scrollable">
              <Tab label="All Pages" />
              {result.page_texts.map((_, i) => (
                <Tab key={i} label={`Page ${i + 1}`} />
              ))}
            </Tabs>
          )}

          {/* Extracted text */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
            <Typography variant="subtitle2">Extracted Text</Typography>
            <Tooltip title={copied ? "Copied!" : "Copy text"}>
              <IconButton size="small" onClick={handleCopy}>
                {copied ? <CheckIcon fontSize="small" color="success" /> : <ContentCopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>
          <TextField
            fullWidth multiline rows={12}
            value={currentText || "(No text detected)"}
            InputProps={{ readOnly: true }}
            size="small"
            sx={{ fontFamily: "monospace" }}
          />
        </Box>
      )}
    </Box>
  );
}
