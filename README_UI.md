# 🏥 Patient Onboarding System - User Guide

## Overview
This AI-powered patient onboarding system automates the processing of patient registration forms and ID proofs using LangGraph and AI.

## Features

### ✨ Core Capabilities
- **📄 Multi-Document Processing**: Upload patient forms and ID proofs simultaneously
- **🤖 AI-Powered Classification**: Automatically identifies document types
- **⚡ Parallel Processing**: OCR and classification run concurrently for speed
- **🔍 Smart Data Extraction**: Extracts structured data from unstructured documents
- **✅ Cross-Validation**: Validates data consistency between ID and form
- **👤 Human-in-the-Loop**: Manual review for edge cases
- **💾 Case Management**: Persistent storage with query capabilities

### 🎨 Enhanced UI Features
- **Real-time Progress Tracking**: Visual feedback for each processing step
- **Interactive Data Comparison**: Side-by-side view of ID vs Form data
- **Validation Dashboard**: Field-level validation with similarity scores
- **Manual Correction Interface**: Edit and revalidate data when needed
- **Export Options**: Download processed data as JSON
- **Case History**: Search and retrieve previous cases

## Getting Started

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file with the required service URLs:
```env
AZURE_OCR_SERVICE_URL=your_ocr_service_url
CLASSIFIER_SERVICE_URL=your_classifier_url
EXTRACTION_SERVICE_URL=your_extraction_url
ADMIN_SERVICE_URL=your_admin_url
METRICS_SERVICE_URL=your_metrics_url
```

### 3. Run the Application
```bash
streamlit run main.py
```

The UI will open in your browser at `http://localhost:8501`

## Using the System

### Step 1: Upload Documents
1. Click on the file uploader
2. Select at least 2 documents:
   - Patient registration form
   - ID proof (Aadhar, Passport, etc.)
3. Supported formats: PDF, PNG, JPG, JPEG

### Step 2: Start Processing
1. Click the **"🚀 Start Processing"** button
2. Watch the progress bar and status updates
3. Each processing step will expand showing details:
   - **📄 Document Processing**: OCR text extraction and classification
   - **🤖 AI Decision**: Document mapping (which is ID vs form)
   - **📋 Template**: Template selection for extraction
   - **🔍 Extraction**: Field-level data extraction
   - **✅ Validation**: Cross-validation of extracted data
   - **💾 Memory**: Case storage

### Step 3: Review Results

#### If Validation Passes ✅
- System shows success message
- Case is automatically saved
- Download options available

#### If Manual Review Required ⚠️
1. Review the comparison table showing mismatches
2. Edit the fields in the correction form
3. Select action:
   - **Revalidate**: Check corrected data
   - **Approve as-is**: Override validation
   - **Reject**: Mark case for rejection
4. Submit corrections

### Step 4: Export Data
- **Download Full State**: Complete state with all processing details
- **Download Extracted Data**: Just the extracted patient information

### Querying Previous Cases
1. Go to sidebar
2. Enter Case ID
3. Click **"Search Case"**
4. View stored case details

## Understanding the Pipeline

### Processing Workflow
```
📤 Upload
    ↓
📄 Document Processing (Parallel)
    - OCR Extraction
    - Document Classification
    ↓
🤖 AI Mapping
    - Identify ID Proof
    - Identify Patient Form
    ↓
📋 Template Selection
    - Fetch appropriate template
    - Get field definitions
    ↓
🔍 Data Extraction
    - Extract from ID Proof
    - Extract from Patient Form
    ↓
✅ Validation
    - Name: 100% match required
    - DOB: 100% match required
    - Address: 80% similarity threshold
    ↓
💾 Memory Storage
```

### Validation Rules
- **Name**: Exact match required (100%)
- **Date of Birth**: Exact match required (100%)
- **Address**: Fuzzy match allowed (80% similarity threshold)

## UI Components

### Main Dashboard
- **File Uploader**: Drag-and-drop or click to upload
- **Process Button**: Initiates the AI pipeline
- **Progress Bar**: Shows overall completion
- **Status Cards**: Real-time node execution updates

### Results Section
- **Processing Results**: Expandable steps showing each node's output
- **Validation Dashboard**: Field-level comparison and match status
- **Summary Metrics**: Quick overview of validation status

### Manual Review Interface
- **Comparison Table**: Shows ID vs Form values side-by-side
- **Edit Form**: Correct mismatched fields
- **Action Selector**: Choose validation action
- **Revalidation**: Instant feedback on corrections

### Sidebar
- **Case Query**: Search for previous cases by ID
- **System Status**: Shows system health
- **Case Details**: View full state of queried cases

## Tips for Best Results

1. **Upload Quality**: Use clear, high-resolution scans
2. **Document Types**: Ensure documents are supported types
3. **Field Matching**: Names should be formatted consistently
4. **Date Formats**: Use standard date formats (DD/MM/YYYY or YYYY-MM-DD)
5. **Address**: Ensure addresses are complete and formatted similarly

## Troubleshooting

### No Results Showing
- Check if external services are reachable
- Verify `.env` configuration
- Check console for error messages

### Validation Failures
- Review extracted data in comparison table
- Check for OCR errors in text extraction
- Use manual review to correct mismatches

### Template Not Found
- Ensure document type is in approved list
- Check admin service connectivity
- Verify template exists for document type

## Advanced Features

### Custom Styling
The UI uses custom CSS for enhanced visual appeal. Modify the CSS in `main.py` to customize appearance.

### Export Formats
Currently supports JSON export. Extend the export section to add CSV, PDF, or other formats.

### Workflow Customization
Modify `agents/graph.py` to add custom nodes or change the workflow logic.

## Support

For issues or questions:
1. Check the console logs for detailed errors
2. Review the node history in the UI
3. Verify all external services are running
4. Check the `.env` configuration

---

**Version**: 1.0  
**Last Updated**: April 3, 2026  
**Powered by**: LangGraph, Streamlit, Google Gemini 2.0
