from typing import TypedDict, List, Optional, Any

class AgentState(TypedDict):
    lease_id: str                 # Unique identifier from Col 13
    current_file_paths: List[str] # List of all files found (PDF, IMG, DOCX)
    file_content: Optional[str]   # The "Digital Twin" JSON (Threaded Fact Sheet)
    audit_results: dict           # The extracted 52 audit answers
    error_log: List[str]          # The continuous trail for Agent 5
    source_found: str             # Track where truth was found (SP vs Local)
    is_locked: bool               # Security flag (encrypted PDFs)
    data_row: dict                # The original Excel context for 3-Way Match
    
    # --- NEW FIELDS FOR AUDIT-GRADE PRECISION ---
    metadata: dict                # NEW: Stores the file manifest (size, page counts)
    is_fragmented: bool           # NEW: Flag for P2-P5-P12 table spills
    evidence_threads: dict        # NEW: The bucketed fragments (Financial vs Termination)