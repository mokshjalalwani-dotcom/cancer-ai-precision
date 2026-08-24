import sys
import json
import pandas as pd
from fastapi.testclient import TestClient

# Add api to path so we can import it
sys.path.append("b:/desktop/Projects/cancerP2")
from api.main import app

def test_2k_genes():
    print("Loading a real patient from the dataset...")
    df = pd.read_csv("b:/desktop/Projects/cancerP2/target_ready_dataset.tsv", sep="\t")
    
    # Take the first patient
    patient = df.iloc[0]
    
    # Get all gene columns
    gene_cols = [c for c in df.columns if c.startswith("ENSG")]
    
    # Take the first 2000 genes
    selected_2k_genes = gene_cols[:2000]
    
    # Build the genes dictionary
    genes_dict = {gene: float(patient[gene]) for gene in selected_2k_genes}
    
    print(f"Extracted {len(genes_dict)} genes.")
    
    payload = {
        "genes": genes_dict
    }
    
    print("\nSending 2000-gene payload to /predict/all...")
    client = TestClient(app)
    
    import time
    start = time.time()
    response = client.post("/predict/all", json=payload)
    duration = time.time() - start
    
    print(f"Response time: {duration:.2f} seconds")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n--- RESULTS ---")
        print(f"Survival Probability: {data['survival_probability']}%")
        print(f"Recurrence Risk: {data['recurrence_probability']}%")
        print(f"Aggressiveness Score: {data['aggressiveness_score']}")
        
        print("\nTop Similar Patients:")
        for neighbor in data['similar_patients']:
            print(f"- {neighbor['case_id']}: Similarity {neighbor['similarity']:.4f}")
            
        print("\nGenerating PDF Report...")
        # Now pass this exact data to the PDF generator
        pdf_response = client.post("/generate-report-pdf", json=data)
        if pdf_response.status_code == 200:
            with open("b:/desktop/Projects/cancerP2/test_2k_report.pdf", "wb") as f:
                f.write(pdf_response.content)
            print("Successfully saved 'test_2k_report.pdf'!")
        else:
            print("PDF generation failed:", pdf_response.text)
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    test_2k_genes()
