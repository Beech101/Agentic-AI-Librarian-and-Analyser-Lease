import fitz  # PyMuPDF
import json
import os
import pandas as pd # You have this installed, let's use it for data structuring
from Short_Term_Brain import AgentState 

def notary_node(state: AgentState):
    """
    Agent 2: The Notary (High-Fidelity Collector)
    Job: Mirroring the physical lease while threading fragmented data across P2-P5-P12.
    """
    l_id = state["lease_id"]
    paths = state.get("current_file_paths", [])
    
    # 1. INITIALIZE MASTER DIGITAL TWIN
    digital_twin = {
        "lease_id": l_id,
        "inventory": [],
        "evidence_threads": {
            "financial_schedules": [], # P2, P5, P12 fragments go here
            "termination_options": [], # All break dates
            "asset_identifiers": []
        }
    }

    print(f"📑 Notary [{l_id}]: Mapping {len(paths)} files with Global Threading...")

    for path in paths:
        if not os.path.exists(path):
            state["error_log"].append(f"Missing File: {path}")
            continue

        file_name = os.path.basename(path)
        ext = path.lower().split('.')[-1]
        
        doc_entry = {"file_name": file_name, "type": ext, "content": []}

        # --- BRANCH A: PDF PROCESSING (High-Signal + Geometry Preservation) ---
        if ext == 'pdf':
            try:
                with fitz.open(path) as doc:
                    total_pages = len(doc)
                    
                    # Selection: First 12 and Last 4 (Your original logic)
                    pages_to_read = sorted(set(list(range(min(12, total_pages))) + list(range(max(0, total_pages-4), total_pages))))

                    for i in pages_to_read:
                        page = doc[i]
                        # We use 'dict' to get coordinates—essential for tables
                        raw_dict = page.get_text("dict")
                        
                        for block in raw_dict["blocks"]:
                            if "lines" in block:
                                # Reconstruct the block text accurately
                                block_text = " ".join([" ".join([span["text"] for span in line["spans"]]) for line in block["lines"]])
                                block_text = block_text.replace('\n', ' ').strip()
                                
                                if not block_text: continue

                                # --- THE THREADING ENGINE ---
                                # This ensures P2, P5, and P12 are linked by topic
                                lower_txt = block_text.lower()
                                evidence_item = {"p": i+1, "txt": block_text, "file": file_name}

                                if any(k in lower_txt for k in ["rent", "cpi", "index", "review", "payment"]):
                                    digital_twin["evidence_threads"]["financial_schedules"].append(evidence_item)
                                elif any(k in lower_txt for k in ["break", "terminate", "option", "notice"]):
                                    digital_twin["evidence_threads"]["termination_options"].append(evidence_item)
                                else:
                                    doc_entry["content"].append(evidence_item)

                print(f"   ✔️  Digitized: {file_name}")

            except Exception as e:
                state["error_log"].append(f"PDF Error [{file_name}]: {str(e)}")

        # --- BRANCH B: IMAGES & WORD (Preserving your safety branches) ---
        elif ext in ['jpg', 'png', 'docx']:
            state["error_log"].append(f"Special Format: {ext} detected for {file_name}. Requires OCR/Word Node.")

        digital_twin["inventory"].append(doc_entry)

    # 3. FINAL OUTPUT
    return {
        "file_content": json.dumps(digital_twin, indent=2),
        "error_log": state["error_log"] + ["Agent 2: Global Evidence Threading Complete."]
    }