Project Overview: Agentic Lease Audit System

Automating IFRS 16 Compliance for 7,200+ Global Contracts
 1. The Two-Tier Strategy

    Tier 1: The Proof of Concept (PoC)

        Objective: To validate LLM capability in extracting 52 audit-critical fields with deterministic precision.

        Function: A high-velocity script designed to transform unstructured legal text into machine-readable JSON schemas, reducing manual processing time by 98%.

        Status: Validated & Functional.

    Tier 2: The Agentic Framework (The Production Build)

        Architecture: A LangGraph-driven orchestration layer utilizing five specialized nodes. This system moves beyond simple extraction by wrapping probabilistic AI outputs in deterministic financial guardrails to ensure 100% audit-readiness

------------------------------------------------------------------------------

 2. Engineering Breakthroughs (The "Surgical Slide")
Surgical GPS Indexing: Solving ID Collision

In complex sub-ledgers, a "Unique ID" represents a sequence, not a single point. A standard AI would see these "duplicates" and hallucinate—potentially dropping 2028 rent data into a 2024 opening balance row.

    The Innovation: I transitioned from Search-by-ID to Direct Row Indexing. The system treats every Excel row as a unique coordinate, allowing for 100% precision in high-density, multi-period contracts where the same Lease ID exists across multiple rows.


Designed a "Digital Amnesia" workflow using isolated AgentState. By resetting the state after every execution cycle, the system removes the risk of cross-contamination or "Memory Hallucinations" between disparate leases.

X-Ray Debugging: Dual-Layer Audit Receipts
The system generates physical JSON "Receipts" for both the Digitization and the Decision Logic. This enables human auditors to instantly verify if a discrepancy originated in the raw text extraction or the legal interpretation.


 3. Personal Impact: Financial Engineering vs. AI Automation

"Most AI implementations in finance fail because they treat data as 'flat'—they extract a number but have no concept of its chronological position in a ledger. I architected the 'Surgical Slide' to solve this."

By treating the Lease ID as the first key and the Extracted Event Date as the second, my Enforcer Node initiates a logical scan across every row sharing an ID. It "slides" through the timeline until it finds the specific window where the document’s date fits mathematically between a row’s Start and End dates.

This is the difference between "AI automation" and Financial Engineering. It turns a fragmented dataset into a high-integrity, audit-ready financial record.


 4. Implementation & Integrity

    Production Velocity: Successfully collapsed 6-month manual audit cycles into 4 weeks.

    Integrity: Stress-tested for high-concurrency scenarios, ensuring system integrity through robust exception-handling protocols.

    Note: Folder pathways are located in the retrieval logic and require redirection for local deployment.
