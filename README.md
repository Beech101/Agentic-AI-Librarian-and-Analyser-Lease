Project Overview: Automated Lease Audit System

This folder contains two architectural tiers designed to automate IFRS 16 compliance audits for a 7,200-row portfolio.
1. The Proof of Concept (PoC)

    Objective: To validate the LLM's ability to extract 52 audit-critical fields with high deterministic accuracy.

    Function: A high-velocity script that transforms unstructured legal text into a machine-readable JSON schema, reducing manual processing time by 98%.

    Status: Validated & Functional.

2. The Agentic AI System (v1.1 - Early Draft)

    Objective: To transition from simple extraction to a fully autonomous, multi-agent workforce.

    Architecture: Utilizes a LangGraph-driven framework to decouple tasks into specialized nodes: Librarian (Retrieval), Notary (Digitization), Analyst (Audit Logic), and Enforcer (Excel Integration).

    Status: Alpha/Early Draft. This version was a foundational blueprint for a self-healing, "Human-in-the-Loop" production system. One of
    the early problems detected in this build was the lack of indempotency. Say for instance a human corrects an entry and you ran the code again
    It can overwrite the users amendmnet. 
