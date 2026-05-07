import os
import json
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from Short_Term_Brain import AgentState

load_dotenv()

# --- 1. LLM CONFIGURATION ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0,
    model_kwargs={"seed": 42, "response_format": {"type": "json_object"}}
)

# --- 2. MASTER AUDIT CONTROLS (Your Command Center) ---
AUDIT_CONTROLS = {
    "20": {"label": "Country", "rule": "Establish correct country. Compare with BDO Valid sheet in Legacy Data."},
    "Currency": {"label": "Currency", "rule": "Contract currency. Must line up with Country currency."},
    "12": {"label": "Effective Start Date", "rule": "Extract from Fact Sheet. If post-acquisition, update to match contract start. Format: DD/MM/YYYY."},
    "13": {"label": "Contract Identifier", "rule": "External name/number. Priority: Number > Name. Max 30 chars, space-separated."},
    "15": {"label": "Sublease", "rule": "Is this a sublease? If yes, output 'check with colleague X', else 'FALSE'."},
    "35": {"label": "Legal Entity", "rule": "Prioritize 'CompanyName' from Legacy Data (Surgery List Column AY)."},
    "Historic Costs": {"label": "Historic Costs", "rule": "If costs are dated before Oct 2021, leave value-driven cells as is."},
    "40": {"label": "Residuals Date", "rule": "Identify residuals date if any. DD/MM/YYYY. If not, leave this blank"},
    "41": {"label": "Residual Values", "rule": "Identify residual value amount if any. If we have no residual value date, leave this blank."},
    "43": {"label": "Transfer of Ownership", "rule": "Identify mentions of Title Transfer. TRUE/FALSE."},
    "46": {"label": "Purchase Option Date", "rule": "Identify date tenant can buy asset. DD/MM/YYYY."},
    "47": {"label": "Purchase Option Value", "rule": "Price to exercise purchase option."},
    "48": {"label": "Option_Exercise_Certainty", "rule": "Is execution reasonably certain? TRUE/FALSE."},
    "51": {"label": "Lease End Date", "rule": "Determine end of holding period (Judgement required based on term)."},
    "53": {"label": "Termination Option Dates", "rule": "Identify all break dates regardless of penalty."},
    "54": {"label": "Termination Option Payment Value", "rule": "Penalty value for early termination."},
    "55": {"label": "Termination Option Payment Date", "rule": "Date penalty is due."},
    "56": {"label": "Break_Certainty_Rating", "rule": "Is the break likely to be executed? TRUE/FALSE."},
    "72": {"label": "Extension Expected", "rule": "Is extension likely to be executed? TRUE/FALSE."},
    "73": {"label": "Extension Execution Payment", "rule": "Rent amount during extension period."},
    "74": {"label": "Extension Execution Payment Date", "rule": "Date extension rent starts. Must be filled in if column 73 contains a value greater than 0."},
    "75": {"label": "Extension End Date", "rule": "Final date of extension period."},
    "77": {"label": "Extension Termination Option Date", "rule": "Break dates available during extension."},
    "78": {"label": "Extension Termination Option Payment", "rule": "Penalty for breaking during extension."},
    "79": {"label": "Extension Termination Option Payment Date", "rule": "Date extension penalty is due."},
    "80": {"label": "Ext_Break_Likelihood", "rule": "Is break termination during extension likely? TRUE/FALSE."},
    "97": {"label": "Initial Costs Amounts", "rule": "Record Deposits/Costs (Excl. security deposits). IFRS16 ONLY."},
    "98": {"label": "Initial Costs Payment Date", "rule": "Date of initial cost payment. IFRS16 ONLY."},
    "101": {"label": "Lease Incentives Amounts", "rule": "Identify incentives/rent-free periods."},
    "102": {"label": "Lease Incentives Payment Date", "rule": "Dates incentives are applied."},
    "103": {"label": "Restoration Costs Amounts", "rule": "Estimated restoration/dilapidation costs."},
    "104": {"label": "Restoration Costs Date", "rule": "Expected restoration date."},
    "114": {"label": "Asset Name", "rule": "Lease Code, Address, Reg, or Model number."},
    "115": {"label": "Asset Description", "rule": "List Key Identifiers (Reg, Model, Address). Do not overfill."},
    "132": {"label": "Comment General", "rule": "Any relevant lease notes not fitting other categories."},
    "134": {"label": "Comment Termination Details", "rule": "Include extension options, auto-extensions, and notice periods."},
    "136": {"label": "Comment Index Binding", "rule": "Indexation details: Type, Base, Increase Point, Review Point."},
    "144": {"label": "Agreement_Amendment_ID", "rule": "Priority: MLC Number > Sublease Number > Address."},
    "145": {"label": "Next Revision CPI Date", "rule": "DD/MM/YYYY. Next revision date relative to today."},
    "146": {"label": "Invoices", "rule": "TRUE if received from landlord; FALSE if manual."},
    "147": {"label": "System_Payment_Method", "rule": "BACs, DD, or SO? Select most likely based on text."},
    "148": {"label": "Sales Tax", "rule": "Is Sales Tax/VAT applicable? TRUE/FALSE."},
    "149": {"label": "File_Audit_Status", "rule": "Reference to original contract subfolder."},
    "150": {"label": "Fixed vs Variable", "rule": "Variable if interest-linked/indexed; Fixed otherwise."},
    "151": {"label": "Insurance", "rule": "TRUE: exists, not incl / FALSE IF PE: exists, incl."},
    "152": {"label": "Property Tax", "rule": "TRUE: exists, not incl / FALSE IF PE: exists, incl."},
    "153": {"label": "Maintenance", "rule": "TRUE: exists, not incl / FALSE IF PE: exists, incl."},
    "154": {"label": "Non_Lease_Charges", "rule": "Format: 'TRUE - [Description]' or FALSE."},
    "155": {"label": "Index_Rate_Type", "rule": "Identify CPI/RPI; otherwise 'None'."},
    "156": {"label": "Notice Period", "rule": "Period required to terminate or exercise options."},
    "157": {"label": "Date Tenant Must Notify", "rule": "DD/MM/YYYY deadline for notification."},
    "158": {"label": "Tax_Recoverable_Flag?", "rule": "TRUE/FALSE."},
    "159": {"label": "Invoice Frequency", "rule": "Monthly, quarterly, bi-annually, or annually."},
    "160": {"label": "Invoice Point", "rule": "In arrears, In month, or In advance?"},
    "161": {"label": "Payment_Split_Flag", "rule": "Format: 'TRUE - [CONTRACT NUMBER ME_P_0000]' or FALSE."},
    "163": {"label": "Data Cleanse Completed", "rule": "Always output TRUE for successfully processed rows."},
    "165": {"label": "Record_Validation_State", "rule": "Always output 'Work in Progress'."}
}

# --- 3. THE ANALYST NODE ---

def analyst_node(state: AgentState):
    l_id = state["lease_id"]
    fact_sheet = state["file_content"]
    legacy_data = state["data_row"]
    row_num = state.get("row_index", "UNKNOWN")

    print(f"🧠 Analyst [{l_id}]: Reconciling Row {row_num}...")

    # Build the rules block
    instruction_block = "\n".join([f"ID {k} | Field: {v['label']} | Rule: {v['rule']}" for k, v in AUDIT_CONTROLS.items()])

    prompt = [
        ("system", "You are an expert IFRS 16 Auditor. You are rigid, precise, and always respond in JSON format."),
        ("user", f"""
        TASK:
        Extract and reconcile 52 audit fields for Lease ID: {l_id}. 
        
        CRITICAL FORMATTING RULE:
        Your response must be a JSON object where the KEYS are the Numeric IDs (e.g., "20", "12", "51").
        Do not use the labels as keys. 

        EVALUATION STEPS:
        1. Look at the FACT SHEET first. 
        2. Check the LEGACY DATA.
        3. If FACT SHEET contradicts LEGACY DATA, prioritize FACT SHEET.
        4. Only use values valid for the timeline in LEGACY DATA.

        AUDIT RULES (Follow these for each ID):
        {instruction_block}

        FACT SHEET (Source Documents):
        {fact_sheet}

        LEGACY DATA (Current Excel Row):
        {legacy_data}
        """)
    ]

    try:
        response = llm.invoke(prompt)
        raw_output = json.loads(response.content)

        # --- 🎯 THE SAFETY MAPPING ---
        final_results = {}
        for key, info in AUDIT_CONTROLS.items():
            label = info['label']
            
            # Try to find the value by Numeric Key first, then by Label
            val = raw_output.get(str(key)) or raw_output.get(label)
            
            # If still null, check if the AI used a slugified version (e.g. "EffectiveStartDate")
            if val is None:
                slug = label.replace(" ", "")
                val = raw_output.get(slug)

            # Assign found value or "(Blank)" to avoid null walls
            final_results[key] = val if val is not None else "(Blank)"

        # --- 💾 EXPORT DECISION ---
        output_dir = r"C:\Users\Daniel\Lease_Project\JSON Agent 3 AUDIT OUTPUTS"
        if not os.path.exists(output_dir): os.makedirs(output_dir)
            
        json_filename = f"ROW_{row_num}_{l_id}_ANALYSIS.json"
        json_path = os.path.join(output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"💾 [EXPORT] AI Decision for Row {row_num} saved.")

        return {
            "audit_results": final_results,
            "error_log": state["error_log"] + [f"Agent 3: Row {row_num} audit analysis complete."]
        }
    except Exception as e:
        print(f"❌ Analyst Error: {e}")
        return {"error_log": state["error_log"] + [f"Analyst Error: {str(e)}"]}