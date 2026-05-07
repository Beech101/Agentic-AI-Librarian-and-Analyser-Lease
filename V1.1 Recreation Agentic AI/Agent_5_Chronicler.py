import pandas as pd
from langgraph.graph import StateGraph, END
from Agent_1_Librarian import librarian_agent
from Agent_2_Notary import notary_node
from Agent_3_Analyst import analyst_node
from Agent_4_Enforcer import enforcer_node # Matches your filename
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
def run_full_audit(limit=5): # Default to 5 for your test run
    print("🚦 Engine: Loading Master Workbook...")
    # Using pyarrow for speed on 7,200 rows
    df = pd.read_excel("Main Validation UK Sheet.xlsx", engine="openpyxl") 
    
    # We target Column 13 (Lease ID) - adjust index if 0-based
    unique_lease_ids = df.iloc[:, 12].dropna().unique() 

    for l_id in unique_lease_ids[:limit]:
        print(f"\n--- 🏁 STARTING LEASE: {l_id} ---")
        
        # --- THE WIPE: Fresh state for every lease ---
        initial_briefcase = {
            "lease_id": str(l_id),
            "current_file_paths": [],
            "file_content": "",
            "audit_results": {},
            "error_log": [],
            "source_found": "None",
            "is_locked": False,
            "data_row": {}, # We'll pull this from the DF if needed
            "metadata": {},
            "is_fragmented": False,
            "evidence_threads": {}
        }

        # --- EXECUTE ---
        try:
            final_state = audit_machine.invoke(initial_briefcase)
            print(f"✅ Finished: {l_id}")
        except Exception as e:
            print(f"❌ Failed: {l_id} | Error: {e}")

if __name__ == "__main__":
    run_full_audit(limit=5) # Set limit to 7200 when ready!