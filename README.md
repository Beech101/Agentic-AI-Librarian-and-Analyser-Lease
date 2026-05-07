Project Overview: Automated Lease Audit System

This folder contains two architectural tiers designed to automate IFRS 16 compliance audits for a 7,200-row portfolio.
1. The Proof of Concept (PoC)

        Objective: To validate the LLM's ability to extract 52 audit-critical fields with high deterministic accuracy.

        Function: A high-velocity script that transforms unstructured legal text into a machine-readable JSON schema, reducing manual processing time by 98%.

        Status: Validated & Functional.

Architecture: A LangGraph-driven framework utilizing four specialized nodes: Librarian (Deep-Scavenger Retrieval), Notary (Multi-Format Digitization), Analyst (Temporal Reconciliation), and Enforcer (Coordinate-Based Integration).

Key Breakthroughs in Error Handling:

        Surgical GPS Indexing: Solved "ID Collision" and "Overwriting" errors. By transitioning from Search-by-ID to Direct Row Indexing, the system treats every Excel row as a unique coordinate. This allows the AI to handle multiple rows for the same Lease ID (e.g., split periods) with 100% precision, preventing data from "bleeding" between different accounting years.

        Temporal Evidence Guardrails: Eliminated "Year-Mixing" inaccuracies. The Analyst is now anchored to the Legacy Data timeline. It uses the existing row dates as a lens, allowing it to scan a 100-page document and ignore any financial values (like Residuals or Rent) that fall outside the specific row's specific accounting window.

        Multi-Stage Evidence Receipts: Implemented a dual-layer audit trail. The system generates physical JSON "Receipts" for both the Digitization (Agent 2) and the Decision Logic (Agent 3). This enables "X-Ray Debugging," allowing humans to instantly verify if a discrepancy originated in the raw text extraction or the legal interpretation.

        State Isolation (The Briefcase Protocol): Designed a "Digital Amnesia" workflow. Each mission is contained in a fresh, isolated AgentState. By resetting the "Briefcase" after every row, the system removes the risk of cross-contamination or "Memory Hallucinations" between different leases.

A cornerstone of this development is continuous stress testing and the iterative engineering of robust exception-handling protocols, ensuring system integrity even under high-concurrency, high-complexity scenarios
