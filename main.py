import streamlit as st
import asyncio
import json
import os
from datetime import datetime
from run import run_agent
from services.validation_service import validate_extracted_data
from services.memory_service import save_case, query_case

# Page configuration
st.set_page_config(
    page_title="Patient Onboarding System",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .node-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        background-color: #f0f2f6;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    /* Dark theme workflow */
    .stApp {
        background-color: #0e1117;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏥 Patient Onboarding System</h1>', unsafe_allow_html=True)
st.markdown("---")

# Add workflow visualization
with st.expander("📊 View Processing Workflow", expanded=False):
    st.markdown("""
    ### Processing Pipeline
    The patient onboarding process follows these steps:
    
    ```
    📤 Upload Documents
        ↓
    📄 Document Processing (OCR + Classification)
        ↓
    🤖 AI Document Mapping (Identify ID vs Form)
        ↓
    📋 Template Selection
        ↓
    🔍 Data Extraction
        ↓
    ✅ Validation (Cross-check ID vs Form)
        ↓
    💾 Save to Memory
    ```
    
    **Key Features:**
    - ⚡ Parallel document processing for speed
    - 🤖 AI-powered document classification
    - ✅ Automatic cross-validation
    - 👤 Manual review for edge cases
    - 💾 Persistent case storage
    """)


# Sidebar - Query previous cases
with st.sidebar:
    st.header("📋 Query Previous Cases")
    st.markdown("---")
    query_id = st.text_input("🔍 Enter Case ID")
    if st.button("Search Case", use_container_width=True):
        case_data = query_case(query_id)
        if case_data:
            st.success(f"✅ Case Found: {query_id}")
            st.write(f"**📅 Timestamp:** {case_data['timestamp']}")
            with st.expander("View Full Case Data"):
                st.json(case_data["state"])
        else:
            st.error("❌ Case not found")
    
    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.info("**Status:** Online ✓")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Documents")
    st.markdown("Please upload **Patient Form** and **ID Proof** documents")
    
with col2:
    st.metric("Documents Required", "2", delta="Upload both")

files = st.file_uploader(
    "Choose files",
    accept_multiple_files=True,
    help="Upload patient registration form and ID proof (e.g., Aadhar, Passport)",
    type=['pdf', 'png', 'jpg', 'jpeg']
)

if files:
    st.success(f"✓ {len(files)} file(s) uploaded successfully")
    for i, file in enumerate(files, 1):
        st.text(f"  {i}. {file.name} ({file.size / 1024:.2f} KB)")

st.markdown("---")


def field_map(extracted_section):
    out = {}
    if not extracted_section:
        return out
    for item in extracted_section.get("extracted_values", []):
        name = item.get("field_name")
        value = item.get("field_value")
        if name:
            out[name.lower()] = value
    return out


def update_field(extracted_section, field_name, new_value):
    if not extracted_section:
        return
    for item in extracted_section.get("extracted_values", []):
        if item.get("field_name", "").lower() == field_name.lower():
            item["field_value"] = new_value
            return
    # if not present, add
    extracted_section.setdefault("extracted_values", []).append({
        "field_name": field_name,
        "normalized_name": field_name,
        "field_value": new_value,
        "confidence": 1.0,
        "page_number": 1,
        "bounding_box": None,
        "extraction_method": "human"
    })




def display_node_status(node_name, status, details=None):
    """Display status for each node with icons and formatting"""
    icons = {
        "async_doc_processing": "📄",
        "llm_decision": "🤖",
        "template": "📋",
        "extraction": "🔍",
        "validation": "✅",
        "memory": "💾",
        "manual_review": "👤"
    }
    
    icon = icons.get(node_name, "⚙️")
    
    if status == "done" or status == "passed":
        st.success(f"{icon} **{node_name.replace('_', ' ').title()}** - Completed")
    elif status == "failed":
        st.error(f"{icon} **{node_name.replace('_', ' ').title()}** - Failed")
    else:
        st.info(f"{icon} **{node_name.replace('_', ' ').title()}** - {status}")
    
    if details:
        with st.expander(f"View {node_name} details"):
            if isinstance(details, dict):
                st.json(details)
            else:
                st.write(details)


def display_extracted_data_table(extracted_data):
    """Display extracted data in a formatted table"""
    id_data_values = {}
    form_data_values = {}
    
    if extracted_data.get("id_data"):
        for item in extracted_data["id_data"].get("extracted_values", []):
            id_data_values[item.get("field_name", "").lower()] = item.get("field_value", "")
    
    if extracted_data.get("form_data"):
        for item in extracted_data["form_data"].get("extracted_values", []):
            form_data_values[item.get("field_name", "").lower()] = item.get("field_value", "")
    
    # Create comparison table
    all_fields = set(list(id_data_values.keys()) + list(form_data_values.keys()))
    
    if all_fields:
        table_data = []
        for field in sorted(all_fields):
            id_val = id_data_values.get(field, "N/A")
            form_val = form_data_values.get(field, "N/A")
            match = "✅ Match" if id_val == form_val and id_val != "N/A" else "⚠️ Mismatch"
            
            table_data.append({
                "Field": field.replace("_", " ").title(),
                "ID Proof": id_val,
                "Patient Form": form_val,
                "Status": match
            })
        
        st.table(table_data)
    else:
        st.warning("No extracted data available")


def display_validation_results(validation_details):
    """Display validation results in a clear format"""
    if not validation_details:
        st.warning("No validation details available")
        return
    
    for detail in validation_details:
        field = detail.get("field", "Unknown")
        matches = detail.get("matches", False)
        similarity = detail.get("similarity", 0)
        threshold = detail.get("threshold", 100)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if matches:
                st.success(f"✅ **{field}**")
            else:
                st.error(f"❌ **{field}**")
        
        with col2:
            st.write(f"Similarity: {similarity}%")
        
        with col3:
            st.write(f"Required: {threshold}%")
        
        with st.expander(f"Details for {field}"):
            st.write(f"**ID Value:** {detail.get('id_value', 'N/A')}")
            st.write(f"**Form Value:** {detail.get('form_value', 'N/A')}")


if st.button("🚀 Start Processing", type="primary", use_container_width=True):
    if not files or len(files) < 2:
        st.error("⚠️ Please upload at least 2 documents (Patient Form and ID Proof)")
    else:
        # Progress tracking
        st.markdown("---")
        
        # Progress bar
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        # Workflow visualization
        st.markdown("### 📊 Processing Workflow")
        workflow_container = st.empty()
        
        # Create node status tracking
        node_status = {
            "process_docs": {"status": "⏳ PENDING", "color": "gray", "done": False},
            "llm_decision": {"status": "⏳ PENDING", "color": "gray", "done": False},
            "template": {"status": "⏳ PENDING", "color": "gray", "done": False},
            "extract": {"status": "⏳ PENDING", "color": "gray", "done": False},
            "validate": {"status": "⏳ PENDING", "color": "gray", "done": False},
            "memory": {"status": "⏳ PENDING", "color": "gray", "done": False},
        }
        
        # Store OCR data for display
        ocr_data = {}
        llm_decision_data = {}
        template_data = {}
        extraction_data = {}
        validation_data = {}
        memory_data = {}
        
        # Counter for unique keys
        update_counter = [0]
        
        def update_workflow_diagram():
            """Update the visual workflow diagram"""
            update_counter[0] += 1
            with workflow_container.container():
                
                # Node 1: Document Processing
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**📄 Document Processing Agent**")
                    st.caption("Performs OCR, classification and field mapping")
                with col2:
                    if node_status['process_docs']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show OCR data if available
                if node_status['process_docs']['done'] and ocr_data:
                    with st.expander("📋 View OCR Results", expanded=False):
                        for doc_id, doc_info in ocr_data.items():
                            doc_type = doc_info.get('document_type', 'Unknown')
                            text = doc_info.get('text', '')
                            
                            st.markdown(f"**Document: {doc_id}**")
                            st.markdown(f"*Type: {doc_type}*")
                            st.text_area(
                                f"OCR Text ({doc_id})", 
                                value=text, 
                                height=150, 
                                key=f"ocr_{doc_id}_{update_counter[0]}",
                                disabled=True
                            )
                            st.markdown("---")
                
                st.markdown("↓")
                
                # Node 2: AI Mapping
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**🤖 AI Document Mapping Agent**")
                    st.caption("Identifies ID proof and patient form")
                with col2:
                    if node_status['llm_decision']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show document mapping if available
                if node_status['llm_decision']['done'] and llm_decision_data:
                    with st.expander("📋 View Document Mapping", expanded=True):
                        st.markdown(f"**ID Proof Document:** `{llm_decision_data.get('id_proof', 'N/A')}`")
                        st.markdown(f"**Patient Form Document:** `{llm_decision_data.get('patient_form', 'N/A')}`")
                
                st.markdown("↓")
                
                # Node 3: Template Agent
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**📋 Template Agent**")
                    st.caption("Selects template")
                with col2:
                    if node_status['template']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show template data if available (right after Template Agent)
                if node_status['template']['done'] and (template_data.get('id_template') or template_data.get('form_template')):
                    with st.expander("📋 View Template Details", expanded=True):
                        id_template = template_data.get('id_template', {})
                        form_template = template_data.get('form_template', {})
                        
                        st.markdown("**ID Proof Template:**")
                        if id_template:
                            st.markdown(f"*Type:* {id_template.get('document_type_name', 'N/A')}")
                            st.markdown(f"*Fields:* {len(id_template.get('field_lists', []))}")
                            if id_template.get('field_lists'):
                                fields_preview = id_template.get('field_lists', [])[:10]
                                for field in fields_preview:
                                    st.markdown(f"- {field.get('field_name', 'Unknown')}")
                                if len(id_template.get('field_lists', [])) > 10:
                                    st.markdown(f"*...and {len(id_template.get('field_lists', [])) - 10} more fields*")
                        else:
                            st.info("No template found")
                        
                        st.markdown("---")
                        
                        st.markdown("**Patient Form Template:**")
                        if form_template:
                            st.markdown(f"*Type:* {form_template.get('document_type_name', 'N/A')}")
                            st.markdown(f"*Fields:* {len(form_template.get('field_lists', []))}")
                            if form_template.get('field_lists'):
                                fields_preview = form_template.get('field_lists', [])[:10]
                                for field in fields_preview:
                                    st.markdown(f"- {field.get('field_name', 'Unknown')}")
                                if len(form_template.get('field_lists', [])) > 10:
                                    st.markdown(f"*...and {len(form_template.get('field_lists', [])) - 10} more fields*")
                        else:
                            st.info("No template found")
                
                st.markdown("↓")
                
                # Node 4: Extraction Agent
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**🔍 Extraction Agent**")
                    st.caption("Extracts fields")
                with col2:
                    if node_status['extract']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show extraction data if available (right after Extraction Agent)
                if node_status['extract']['done'] and extraction_data:
                    with st.expander("🔍 View Extracted Data", expanded=True):
                        id_data = extraction_data.get('id_data', {})
                        form_data = extraction_data.get('form_data', {})
                        
                        st.markdown("**ID Proof Data:**")
                        if id_data.get('extracted_values'):
                            for item in id_data['extracted_values'][:10]:
                                st.markdown(f"- **{item.get('field_name')}:** {item.get('field_value')}")
                            if len(id_data.get('extracted_values', [])) > 10:
                                st.markdown(f"*...and {len(id_data.get('extracted_values', [])) - 10} more fields*")
                        else:
                            st.info("No data extracted yet")
                        
                        st.markdown("---")
                        
                        st.markdown("**Patient Form Data:**")
                        if form_data.get('extracted_values'):
                            for item in form_data['extracted_values'][:10]:
                                st.markdown(f"- **{item.get('field_name')}:** {item.get('field_value')}")
                            if len(form_data.get('extracted_values', [])) > 10:
                                st.markdown(f"*...and {len(form_data.get('extracted_values', [])) - 10} more fields*")
                        else:
                            st.info("No data extracted yet")
                
                st.markdown("↓")
                
                # Node 5: Validation
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**✅ Validation Agent**")
                    st.caption("Cross-validates ID with form")
                with col2:
                    if node_status['validate']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show validation results if available
                if node_status['validate']['done'] and validation_data:
                    status = validation_data.get('status', 'unknown')
                    is_passed = status == 'passed'
                    
                    with st.expander(f"{'✅' if is_passed else '❌'} View Validation Results", expanded=True):
                        st.markdown(f"**Status:** {'✅ PASSED' if is_passed else '❌ FAILED'}")
                        st.markdown(f"**Summary:** {validation_data.get('summary', 'N/A')}")
                        
                        if validation_data.get('validation_details'):
                            st.markdown("**Field-by-Field Comparison:**")
                            for detail in validation_data['validation_details']:
                                field = detail.get('field', 'Unknown')
                                matches = detail.get('matches', False)
                                similarity = detail.get('similarity', 0)
                                threshold = detail.get('threshold', 100)
                                
                                icon = "✅" if matches else "❌"
                                st.markdown(f"{icon} **{field}:** {similarity}% (Threshold: {threshold}%)")
                
                st.markdown("↓")
                
                # Node 6: Memory
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**💾 Onboarding Agent**")
                    st.caption("Saves patient details")
                with col2:
                    if node_status['memory']['done']:
                        st.success("✅ DONE")
                    else:
                        st.info("⏳ PENDING")
                
                # Show memory save results if available
                if node_status['memory']['done'] and memory_data:
                    with st.expander("💾 View Saved Data", expanded=True):
                        st.markdown(f"**Case ID:** `{memory_data.get('case_id', 'N/A')}`")
                        st.markdown(f"**Status:** Patient data successfully saved to memory")
                        
                        if memory_data.get('patient_data'):
                            st.markdown("**Patient Information:**")
                            patient_info = memory_data['patient_data']
                            st.json(patient_info)
        
        # Initial render
        update_workflow_diagram()
        
        # Node counter for progress
        completed_nodes = [0]
        total_expected_nodes = 6
        
        # Define callback for progress updates
        def progress_callback(node_name, node_state):
            completed_nodes[0] += 1
            progress = min(int((completed_nodes[0] / total_expected_nodes) * 100), 100)
            progress_bar.progress(progress)
            progress_text.text(f"🔄 Processing: {node_name.replace('_', ' ').title()}...")
            
            # Update node status
            if node_name in node_status:
                node_status[node_name]['done'] = True
                node_status[node_name]['status'] = '✅ DONE'
                node_status[node_name]['color'] = '#28a745'
            
            # Capture data from each node
            if node_name == "process_docs":
                documents = node_state.get("documents", {})
                for doc_id, doc_info in documents.items():
                    ocr_data[doc_id] = doc_info
            
            elif node_name == "llm_decision":
                doc_mapping = node_state.get("doc_mapping", {})
                llm_decision_data['id_proof'] = doc_mapping.get('id_proof', 'N/A')
                llm_decision_data['patient_form'] = doc_mapping.get('patient_form', 'N/A')
            
            elif node_name == "template":
                templates = node_state.get("templates", {})
                if templates:
                    template_data['id_template'] = templates.get('id_template', {})
                    template_data['form_template'] = templates.get('form_template', {})
            
            elif node_name == "extract":
                extracted = node_state.get("extracted_data", {})
                if extracted:
                    extraction_data['id_data'] = extracted.get('id_data', {})
                    extraction_data['form_data'] = extracted.get('form_data', {})
            
            elif node_name == "validate":
                validation_data['status'] = node_state.get('validation_status', 'unknown')
                validation_data['validation_details'] = node_state.get('validation_details', [])
                validation_data['summary'] = 'All fields validated' if validation_data['status'] == 'passed' else 'Validation failed'
            
            elif node_name == "memory":
                memory_data['case_id'] = node_state.get('case_id', 'N/A')
                memory_data['patient_data'] = node_state.get('extracted_data', {})
            
            # Update the workflow diagram
            update_workflow_diagram()
        
        # Execute the agent with progress callback
        async def run_with_progress():
            return await run_agent(files, progress_callback=progress_callback)
        
        state = asyncio.run(run_with_progress())
        
        progress_bar.progress(100)
        progress_text.text("✅ Processing Complete!")
        
        # Add detailed results section
        st.markdown("---")
        st.subheader("📊 Detailed Results")
        
        # Show validation details if available
        if state.get("validation_details"):
            with st.expander("✅ Validation Details", expanded=False):
                display_validation_results(state.get("validation_details"))
        
        # Final summary
        st.markdown("---")
        st.subheader("📈 Final Summary")
        
        validation_status = state.get("validation_status", "unknown")
        manual_review = state.get("manual_review_required", False)
        case_id = state.get("case_id", "Not saved")
        node_history = state.get("node_history", [])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if validation_status == "passed":
                st.metric("Validation Status", "✅ Passed", delta="Success")
            else:
                st.metric("Validation Status", "❌ Failed", delta="Review Required")
        
        with col2:
            st.metric("Total Steps", len(node_history))
        
        with col3:
            if case_id != "Not saved":
                st.metric("Case ID", case_id)
            else:
                st.metric("Case ID", "-")
        
        # Manual review section
        if manual_review or validation_status != "passed":
            st.markdown("---")
            st.markdown("### 👤 Manual Review Required")
            st.warning("⚠️ Some fields require correction. Please review and update below.")
            
            id_data = field_map(state.get("extracted_data", {}).get("id_data", {}))
            form_data = field_map(state.get("extracted_data", {}).get("form_data", {}))

            st.markdown("#### 📝 Current Extracted Data")
            
            # Show current data in comparison
            comparison_data = []
            for field in ["name", "date_of_birth", "address"]:
                id_val = id_data.get(field, "")
                form_val = form_data.get(field, "")
                match_status = "✅ Match" if id_val == form_val else "❌ Mismatch"
                comparison_data.append({
                    "Field": field.replace("_", " ").title(),
                    "ID Value": id_val,
                    "Form Value": form_val,
                    "Status": match_status
                })
            
            st.table(comparison_data)

            st.markdown("#### ✏️ Correct the Data")
            with st.form("hitl_form"):
                st.markdown("**Edit the fields below and revalidate:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("👤 Full Name", value=id_data.get("name", ""), 
                                        help="Enter the patient's full name")
                    dob = st.text_input("📅 Date of Birth", value=id_data.get("date_of_birth", ""),
                                       help="Format: DD/MM/YYYY or YYYY-MM-DD")
                
                with col2:
                    address = st.text_area("🏠 Address", value=id_data.get("address", ""),
                                          height=100,
                                          help="Enter complete address")
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    action = st.selectbox("⚡ Action", 
                                        ["revalidate", "approve_as_is", "reject"],
                                        help="Choose what to do with the corrected data")
                
                with col2:
                    st.write("")  # Spacer
                
                with col3:
                    st.write("")  # Spacer
                
                submit = st.form_submit_button("✅ Submit Corrections", use_container_width=True, type="primary")

            if submit:
                # update both id and form fields (human-corrected canonical value)
                for field, value in [("name", name), ("date_of_birth", dob), ("address", address)]:
                    update_field(state["extracted_data"]["id_data"], field, value)
                    update_field(state["extracted_data"]["form_data"], field, value)

                if action == "reject":
                    state["validation_status"] = "rejected"
                    state["manual_review_required"] = True
                    st.error("❌ Case rejected manually.")
                else:
                    with st.spinner("🔄 Revalidating data..."):
                        validation_result = validate_extracted_data(state["extracted_data"])
                        state["validation_status"] = validation_result.get("status", "failed")
                        state["validation_details"] = validation_result.get("validation_details", [])
                        state["manual_review_required"] = state["validation_status"] != "passed"

                    st.markdown("### 🔍 Re-validation Result")
                    
                    if state["validation_status"] == "passed":
                        st.success("✅ Validation Passed!")
                        st.balloons()
                    else:
                        st.error("❌ Validation still failed")
                    
                    display_validation_results(validation_result.get("validation_details", []))

                    # Show updated data in table format after revalidation
                    st.markdown("### 📊 Updated Extracted Data")
                    id_data = field_map(state["extracted_data"]["id_data"])
                    form_data = field_map(state["extracted_data"]["form_data"])
                    
                    updated_comparison = []
                    for field in ["name", "date_of_birth", "address"]:
                        id_val = id_data.get(field, "")
                        form_val = form_data.get(field, "")
                        match_status = "✅ Match" if id_val == form_val else "❌ Mismatch"
                        updated_comparison.append({
                            "Field": field.replace("_", " ").title(),
                            "ID Value": id_val,
                            "Form Value": form_val,
                            "Status": match_status
                        })
                    
                    st.table(updated_comparison)

                    if state["validation_status"] == "passed":
                        st.success("✅ Validation passed; ready to continue downstream.")
                        # Save to persistent memory
                        name = field_map(state["extracted_data"]["id_data"]).get("name", "unknown")
                        from datetime import datetime
                        case_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        save_case(case_id, state)
                        st.info(f"💾 Case saved with ID: **{case_id}**")
                    else:
                        st.warning("⚠️ Still failed after correction; please review again.")

        else:
            st.success("✅ All validations passed automatically. No manual review needed!")

        # Enforce memory persistence if validations passed but in-graph save might have been skipped
        final_case_id = state.get("case_id")
        memory_saved = state.get("memory_saved", False)
        if validation_status == "passed" and not memory_saved:
            name = field_map(state.get("extracted_data", {}).get("id_data", {})).get("name", "unknown")
            final_case_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            save_case(final_case_id, state)
            state["case_id"] = final_case_id
            state["memory_saved"] = True
            st.info(f"💾 Case saved to persistent memory with ID: **{final_case_id}**")
        elif memory_saved:
            st.info(f"✓ Case already persisted: **{final_case_id}**")
        
        # Download option for final state
        st.markdown("---")
        st.markdown("### 📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as JSON
            final_state_json = json.dumps(state, indent=2, default=str)
            st.download_button(
                label="📄 Download Full State (JSON)",
                data=final_state_json,
                file_name=f"patient_case_{final_case_id}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Export extracted data only
            extracted_summary = {
                "case_id": final_case_id,
                "timestamp": datetime.now().isoformat(),
                "validation_status": validation_status,
                "extracted_data": state.get("extracted_data", {})
            }
            summary_json = json.dumps(extracted_summary, indent=2, default=str)
            st.download_button(
                label="📋 Download Extracted Data",
                data=summary_json,
                file_name=f"extracted_data_{final_case_id}.json",
                mime="application/json",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🏥 Patient Onboarding System | Powered by AI & LangGraph</p>
    </div>
    """,
    unsafe_allow_html=True
)

