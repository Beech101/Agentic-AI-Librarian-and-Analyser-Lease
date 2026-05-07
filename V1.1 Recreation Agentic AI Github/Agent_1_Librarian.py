import os
import fitz  # PyMuPDF
import datetime
from langgraph.graph import StateGraph, END
from Short_Term_Brain import AgentState 

# --- 2. AGENT 1: THE LIBRARIAN NODES ---

def check_sharepoint_hierarchy(state: AgentState):
    """
    Theoretical Node: Hierarchical Cloud Search.
    Logic: Checks NEW repository, then OLD repository.
    """
    l_id = state["lease_id"]
    print(f"🔍 Librarian [{l_id}]: Initiating Cloud Search (NEW -> OLD)...")

    # Placeholder for actual SharePoint API integration
    # Returning "None" triggers the fallback to local repository
    return {
        "source_found": "None", 
        "error_log": state["error_log"] + [f"[{datetime.datetime.now()}] SharePoint: No match. Shifting to Local."]
    }

def check_local_repository(state: AgentState):
    """
    The Deep Scavenger: Digs through the Lease folder and all its subfolders 
    to find every single file.
    """
    l_id = str(state["lease_id"])
    lease_root = "./Leases" 
    target_subfolder = os.path.join(lease_root, l_id)
    
    if os.path.exists(target_subfolder) and os.path.isdir(target_subfolder):
        all_files = []
        
        # 🕵️ os.walk "walks" into every subfolder (like 'contract details')
        for root, dirs, files in os.walk(target_subfolder):
            for f in files:
                full_path = os.path.join(root, f)
                all_files.append(full_path)
        
        if not all_files:
            return {
                "source_found": "EMPTY_FOLDER",
                "error_log": state["error_log"] + [f"CRITICAL: Subfolder '{l_id}' exists but no files were found inside."]
            }

        # 🔍 Print to console so you can see it working!
        print(f"📁 Librarian found {len(all_files)} files in {l_id}:")
        for f in all_files:
            print(f"   - {os.path.basename(f)}")

        return {
            "current_file_paths": all_files,
            "source_found": "Local_Subfolder",
            "error_log": state["error_log"] + [f"SUCCESS: Located {len(all_files)} files in '{l_id}'."]
        }

    return {
        "source_found": "NOT_FOUND", 
        "error_log": state["error_log"] + [f"CRITICAL: Lease ID folder '{l_id}' missing."]
    }

def validate_manifest_integrity(state: AgentState):
    """
    The Inspector: Verifies file health and creates the 'Manifest' for Agent 5.
    """
    paths = state.get("current_file_paths", [])
    manifest = []
    locked_files = []
    corrupt_files = []
    
    for path in paths:
        f_name = os.path.basename(path)
        f_size = os.path.getsize(path) / 1024  # KB
        
        # 🧪 CORRUPTION & ENCRYPTION TEST
        if path.lower().endswith(".pdf"):
            try:
                with fitz.open(path) as doc:
                    if doc.is_encrypted:
                        locked_files.append(f_name)
                    # Create metadata for the "Briefcase"
                    manifest.append({
                        "name": f_name,
                        "size_kb": round(f_size, 2),
                        "pages": len(doc),
                        "status": "Ready"
                    })
            except Exception:
                corrupt_files.append(f_name)
        else:
            # Non-PDF files (images/docx) are just added to manifest
            manifest.append({"name": f_name, "size_kb": round(f_size, 2), "status": "Pending_OCR"})

    # Determine if we can proceed
    success_gate = len(corrupt_files) == 0
    
    return {
        "is_locked": len(locked_files) > 0,
        "error_log": state["error_log"] + [
            f"Inspector: {len(manifest)} files verified. Corrupt: {len(corrupt_files)} | Locked: {len(locked_files)}"
        ],
        # We store the detailed manifest so Agent 2 knows exactly what to expect
        "metadata": {"manifest": manifest, "corrupt_list": corrupt_files}
    }

# --- 3. THE ROUTER (The 'GPS' Logic) ---

def librarian_router(state: AgentState):
    if state["source_found"] == "Local_Subfolder":
        return "validate"
    if state["source_found"] == "None":
        return "check_local"
    return END

# --- 4. CONSTRUCT THE GRAPH ---

workflow = StateGraph(AgentState)

workflow.add_node("check_sp", check_sharepoint_hierarchy)
workflow.add_node("check_local", check_local_repository)
workflow.add_node("validate", validate_manifest_integrity)

workflow.set_entry_point("check_sp")

workflow.add_conditional_edges("check_sp", librarian_router, {
    "check_local": "check_local", 
    "validate": "validate",
    END: END
})

workflow.add_edge("check_local", "validate")
workflow.add_edge("validate", END)

librarian_agent = workflow.compile()