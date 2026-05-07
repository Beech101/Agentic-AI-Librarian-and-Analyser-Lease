import fitz  # PyMuPDF
import json
import os
from docx import Document 
from Short_Term_Brain import AgentState 

def notary_node(state: AgentState):
    """
    Agent 2: The Notary (High-Fidelity Collector)
    Job: Aggressively threads data to ensure Agent 3 hits all 52 audit fields.
    """
    l_id = state["lease_id"]
    paths = state.get("current_file_paths", [])
    
    digital_twin = {
        "lease_id": l_id,
        "inventory": [],
        "evidence_threads": {
            "financial_schedules": [],  # For Fields: 73, 97, 101, 103, 148, 150-154, 159-161
            "temporal_options": [],      # For Fields: 12, 40, 46, 51, 53, 55, 74, 75, 77, 79, 98, 102, 104, 145, 156, 157
            "asset_and_parties": []      # For Fields: 20, Currency, 13, 15, 35, 114, 115, 144
        }
    }

    print(f"📑 Notary [{l_id}]: Mapping {len(paths)} files with Aggressive Threading...")

    for path in paths:
        if not os.path.exists(path):
            state["error_log"].append(f"Missing File: {path}")
            continue

        file_name = os.path.basename(path)
        ext = path.lower().split('.')[-1]
        doc_entry = {"file_name": file_name, "type": ext, "content": []}

        # --- 1. KEYWORD TRIGGER CLUSTERS ---
        # Money/Costs/Frequency
        fin_keys = ["£", "$", "€", "rent", "payment", "amount", "sum", "vat", "tax", "cpi", "index", "review", "insurance", "charge", "cost", "incentive", "arrears", "advance", "frequency"]
        # Dates/Duration/Options
        temp_keys = ["date", "term", "year", "month", "day", "commence", "start", "end", "expiry", "period", "notice", "duration", "break", "terminate", "option", "certainty", "extension", "renewal"]
        # Names/Places/IDs
        asset_keys = ["landlord", "tenant", "party", "parties", "ltd", "limited", "address", "premises", "unit", "estate", "schedule", "registered", "country", "currency", "sublease", "entity", "asset", "reg"]

        # --- BRANCH A: PDF ---
        if ext == 'pdf':
            try:
                with fitz.open(path) as doc:
                    total_pages = len(doc)
                    pages_to_read = sorted(set(list(range(min(12, total_pages))) + list(range(max(0, total_pages-4), total_pages))))
                    for i in pages_to_read:
                        page = doc[i]
                        raw_dict = page.get_text("dict")
                        for block in raw_dict["blocks"]:
                            if "lines" in block:
                                block_text = " ".join([" ".join([span["text"] for span in line["spans"]]) for line in block["lines"]])
                                block_text = block_text.replace('\n', ' ').strip()
                                if not block_text: continue

                                lower_txt = block_text.lower()
                                ev_item = {"p": i+1, "txt": block_text, "file": file_name}

                                if any(k in lower_txt for k in fin_keys):
                                    digital_twin["evidence_threads"]["financial_schedules"].append(ev_item)
                                elif any(k in lower_txt for k in temp_keys):
                                    digital_twin["evidence_threads"]["temporal_options"].append(ev_item)
                                elif any(k in lower_txt for k in asset_keys):
                                    digital_twin["evidence_threads"]["asset_and_parties"].append(ev_item)
                                else:
                                    doc_entry["content"].append(ev_item)
                print(f"   ✔️  PDF Digitized: {file_name}")
            except Exception as e:
                state["error_log"].append(f"PDF Error [{file_name}]: {str(e)}")

        # --- BRANCH B: WORD ---
        elif ext == 'docx':
            try:
                doc = Document(path)
                for para_num, para in enumerate(doc.paragraphs):
                    text = para.text.strip()
                    if not text: continue
                    lower_txt = text.lower()
                    ev_item = {"p": f"Para {para_num+1}", "txt": text, "file": file_name}

                    if any(k in lower_txt for k in fin_keys):
                        digital_twin["evidence_threads"]["financial_schedules"].append(ev_item)
                    elif any(k in lower_txt for k in temp_keys):
                        digital_twin["evidence_threads"]["temporal_options"].append(ev_item)
                    elif any(k in lower_txt for k in asset_keys):
                        digital_twin["evidence_threads"]["asset_and_parties"].append(ev_item)
                    else:
                        doc_entry["content"].append(ev_item)
                print(f"   ✔️  Word Doc Digitized: {file_name}")
            except Exception as e:
                state["error_log"].append(f"Word Error [{file_name}]: {str(e)}")

        digital_twin["inventory"].append(doc_entry)

    # --- 💾 EXPORT ---
    output_dir = r"C:\Users\Daniel\Lease_Project\JSON Agent 2 AUDIT OUTPUTS"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    json_path = os.path.join(output_dir, f"{l_id}_audit_source.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(digital_twin, f, indent=2)
    
    print(f"💾 [EXPORT] Source Data saved to: {l_id}_audit_source.json")

    return {
        "file_content": json.dumps(digital_twin, indent=2),
        "error_log": state["error_log"] + ["Agent 2: Aggressive Multi-Format Threading Complete."]
    }