import os
import fitz
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0,
    model_kwargs={"seed": 42, "response_format": {"type": "json_object"}}
)

# --- SETTINGS ---
lease_folder = "./Leases"
output_file = "BDO_Full_Validation_Export.xlsx"

# 1. THE COMPLETE MAPPING (All your anchor points)
audit_mapping = {
    "20": "Country",
    "Currency": "Currency",
    "12": "Effective Start Date",
    "13": "Contract Identifier",
    "15": "Sublease",
    "35": "Legal Entity",
    "40": "Residuals Date",
    "41": "Residual Values",
    "43": "Transfer of Ownership",
    "46": "Purchase Option Date",
    "47": "Purchase Option Value",
    "48": "Purchase Option Expected",
    "51": "Lease End Date",
    "53": "Termination Option Dates",
    "54": "Termination Payment Value",
    "55": "Termination Payment Date",
    "56": "Termination Execution Expected",
    "72": "Extension Expected",
    "73": "Extension Payment",
    "74": "Extension Payment Date",
    "75": "Extension End Date",
    "77": "Ext Termination Date",
    "78": "Ext Termination Payment",
    "79": "Ext Termination Payment Date",
    "80": "Ext Termination Expected",
    "97": "Initial Costs Amounts",
    "98": "Initial Costs Date",
    "101": "Lease Incentives Amounts",
    "102": "Lease Incentives Date",
    "103": "Restoration Costs Amounts",
    "104": "Restoration Costs Date",
    "114": "Asset Name",
    "115": "Asset Description",
    "132": "Comment General",
    "134": "Comment Termination Details",
    "136": "Comment Index Binding",
    "144": "Revision Agreement Number",
    "145": "Next Revision CPI Date",
    "146": "Invoices",
    "147": "Payment Type",
    "148": "Sales Tax Applicable",
    "149": "Document Status",
    "150": "Fixed vs Variable",
    "151": "Insurance",
    "152": "Property Tax",
    "153": "Maintenance",
    "154": "Non-Lease Payments",
    "155": "Applicable Index",
    "156": "Notice Period",
    "157": "Date Tenant Must Notify",
    "158": "Sales Tax Recoverable",
    "159": "Invoice Frequency",
    "160": "Invoice Point",
    "161": "Split Landlord",
    "163": "Data Cleanse Completed",
    "165": "Validation Status"
}

def get_high_signal_text(path):
    context = ""
    try:
        with fitz.open(path) as doc:
            # We need more context for 50+ fields, so we read more pages
            pages = list(range(min(12, len(doc)))) + list(range(max(0, len(doc)-4), len(doc)))
            for i in sorted(set(pages)):
                context += f"\n--- PAGE {i+1} ---\n{doc[i].get_text()}"
        return context[:35000] # Increased limit for huge field list
    except Exception as e: return str(e)

# --- MAIN ENGINE ---
all_results = []
row_1 = {**{"File Name": "File Name"}, **{k: k for k in audit_mapping.keys()}}
row_2 = {**{"File Name": "File Name"}, **{k: v for k, v in audit_mapping.items()}}

for filename in os.listdir(lease_folder):
    if filename.endswith(".pdf"):
        print(f"🕵️ Full Deep Audit: {filename}")
        context = get_high_signal_text(os.path.join(lease_folder, filename))
        
        prompt = [
            ("system", "You are a professional IFRS 16 Auditor. Return ONLY valid JSON."),
            ("user", f"""Extract every single one of these fields from the text. Use 'null' if not found.
            Dates: DD/MM/YYYY. 
            Booleans: TRUE/FALSE.
            
            Fields to find: {list(audit_mapping.values())}
            
            CONTEXT:
            {context}""")
        ]
        
        try:
            response = llm.invoke(prompt)
            raw_data = json.loads(response.content)
            
            mapped_data = {"File Name": filename}
            for num, desc in audit_mapping.items():
                val = raw_data.get(desc) or raw_data.get(num)
                mapped_data[num] = val
                
            all_results.append(mapped_data)
        except Exception as e:
            print(f"❌ Error {filename}: {e}")

# --- EXCEL GENERATION ---
if all_results:
    df_data = pd.DataFrame(all_results)
    df_row1 = pd.DataFrame([row_1])
    df_row2 = pd.DataFrame([row_2])
    
    final_df = pd.concat([df_row1, df_row2, df_data], ignore_index=True)
    final_df.to_excel(output_file, index=False, header=False)
    print(f"\n🏆 FULL AUDIT COMPLETE! {output_file} now contains all {len(audit_mapping)} fields.")