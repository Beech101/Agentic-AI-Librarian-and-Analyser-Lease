import pandas as pd
import json
from langgraph.graph import StateGraph, END
from Agent_1_Librarian import librarian_agent
from Agent_2_Notary import notary_node
from Agent_3_Analyst import analyst_node
from Agent_4_Enforcer import enforcer_node
from Short_Term_Brain import AgentState

# --- 1. CONSTRUCT THE MASTER ASSEMBLY LINE ---
builder = StateGraph(AgentState)
builder.add_node("librarian", librarian_agent)
builder.add_node("notary", notary_node)
builder.add_node("analyst", analyst_node)
builder.add_node("enforcer", enforcer_node)

builder.set_entry_point("librarian")
builder.add_edge("librarian", "notary")
builder.add_edge("notary", "analyst")
builder.add_edge("analyst", "enforcer")
builder.add_edge("enforcer", END)

audit_machine = builder.compile()

# --- 2. THE 7,200 ROW CONTROLLER ---
def run_full_audit(limit=5):
    print("🚦 Engine: Loading Master Workbook...")
    
    # header=0 reads Row 1 as the column names
    df = pd.read_excel("Main Validation UK Sheet.xlsx", engine="openpyxl", header=0) 
    
    # 🎯 STEP 1: Find Anchor '7' (Type Insensitive)
    anchor_col = None
    for col in df.columns:
        if str(col).strip() == "7":
            anchor_col = col
            break
    
    if anchor_col is None:
        print(f"❌ Error: Could not find anchor '7' in Row 1. Headers seen: {list(df.columns[:5])}")
        return

    # 🎯 STEP 2: Skip Row 2 and 3 (The 'Non-empty' and 'Label' rows)
    # Slicing from index 2 starts us at Excel Row 4.
    df_clean = df.iloc[2:].copy()

    print(f"🗂️ Sorting Leases Alphabetically by {anchor_col}...")
    df_sorted = df_clean.sort_values(by=anchor_col, ascending=True)

    # 🎯 STEP 3: The Surgical Loop
    # We iterate through EVERY row. No .unique() here, so we catch split-row duplicates.
    count = 0
    for i, row in df_sorted.iterrows():
        if count >= limit:
            break
            
        l_id = str(row[anchor_col])
        if pd.isna(l_id) or l_id.lower() == "nan":
            continue

        # 🎯 THE GPS MATH:
        # Pandas index 'i' (starting at 2) + 2 = Excel Row 4.
        excel_row_num = i + 2 

        print(f"\n--- 🏁 STARTING MISSION: {l_id} | EXCEL ROW: {excel_row_num} ---")
        
        initial_briefcase = {
            "lease_id": l_id,
            "row_index": excel_row_num,        # For Agent 4 (The Enforcer)
            "data_row": row.to_json(),         # For Agent 3 (The Analyst)
            "current_file_paths": [],
            "file_content": "",
            "audit_results": {},
            "error_log": [],
            "source_found": "None",
            "is_locked": False,
            "metadata": {},
            "is_fragmented": False,
            "evidence_threads": {}
        }

        try:
            audit_machine.invoke(initial_briefcase)
            print(f"✅ Finished: {l_id} (Row {excel_row_num})")
        except Exception as e:
            print(f"❌ Failed: {l_id} | Error: {e}")
        
        count += 1

if __name__ == "__main__":
    # Change limit to 7200 for the final run
    run_full_audit(limit=5)