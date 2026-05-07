from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    lease_id: str                 # Unique identifier from Col 13
    current_file_paths: List[str]  # List of all files found (PDF, IMG, DOCX)
    file_content: Optional[str]    # The "Digital Twin" JSON created by Agent 2 (The Fact Sheet)
    audit_results: dict            # The extracted 52 audit answers from Agent 3 (The Analyst)
    error_log: List[str]          # The continuous trail for Agent 5 (The Chronicler)
    source_found: str             # Track where we found the truth (SP vs Local)
    is_locked: bool               # Security flag (encrypted PDFs detected by Agent 1)
    data_row: dict                # The original Excel context for the 3-Way Match