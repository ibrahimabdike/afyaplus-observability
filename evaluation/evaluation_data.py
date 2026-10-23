# evaluation_data.py
import pandas as pd

CLINICAL_EVALUATION_DATA = [
    # USSD Channel (5 questions)
    {
        "question": "A 45-year-old patient reports persistent chest pain and shortness of breath. What is the triage protocol?",
        "reference": "For chest pain with dyspnea, immediate emergency referral is required. Perform ECG within 10 minutes, administer aspirin 300mg if not contraindicated, and transfer to cardiac care unit.",
        "channel": "USSD",
        "feature": "triage_advisor"
    },
    {
        "question": "What are the Ministry of Health guidelines for malaria treatment in pregnant women?",
        "reference": "First-trimester pregnant women with uncomplicated malaria should receive quinine + clindamycin. Second/third trimester: artemether-lumefantrine is preferred. Severe malaria requires IV artesunate regardless of trimester.",
        "channel": "USSD",
        "feature": "clinical_protocols"
    },
    {
        "question": "A child presents with fever, rash, and conjunctivitis. What is the differential diagnosis?",
        "reference": "Consider measles (Koplik spots, coryza, cough), Kawasaki disease (prolonged fever, strawberry tongue, cervical lymphadenopathy), or scarlet fever (strawberry tongue, pastia lines, circumoral pallor).",
        "channel": "USSD",
        "feature": "triage_advisor"
    },
    {
        "question": "What is the correct dosage of oral rehydration solution for a 2-year-old with diarrhea?",
        "reference": "For mild-moderate dehydration: 50-100ml/kg over 4 hours. For severe dehydration: 100ml/kg over 6 hours. Give 5-10ml of ORS every 5-10 minutes if vomiting is present.",
        "channel": "USSD",
        "feature": "clinical_protocols"
    },
    {
        "question": "How should a healthcare worker manage a needlestick injury exposure?",
        "reference": "Immediate first aid: wash wound with soap and water, apply antiseptic. Baseline HIV/HBV/HCV testing for source and exposed. Start PEP within 72 hours for HIV if source is high-risk.",
        "channel": "USSD",
        "feature": "safety_protocols"
    },
    
    # Mobile App Channel (5 questions)
    {
        "question": "What are the clinical criteria for initiating antiretroviral therapy in HIV patients?",
        "reference": "Initiate ART immediately upon diagnosis regardless of CD4 count. Preferred regimen: TDF/3TC/DTG. Monitor viral load at 6 months and annually. CD4 monitoring is no longer required for treatment initiation.",
        "channel": "Mobile App",
        "feature": "clinical_protocols"
    },
    {
        "question": "A hypertensive patient on amlodipine presents with ankle edema. What is the management approach?",
        "reference": "Ankle edema is a common amlodipine side effect. Consider switching to a different CCB (e.g., lercanidipine), reducing the dose if BP permits, or adding an ACE inhibitor. Rule out heart failure and nephrotic syndrome.",
        "channel": "Mobile App",
        "feature": "clinical_protocols"
    },
    {
        "question": "What are the WHO danger signs in children under 5 years?",
        "reference": "WHO danger signs: convulsions, lethargy/unconsciousness, inability to drink or breastfeed, vomiting everything, severe dehydration, respiratory distress, severe malnutrition, and signs of sepsis.",
        "channel": "Mobile App",
        "feature": "triage_advisor"
    },
    {
        "question": "How should tuberculosis treatment be adjusted in patients with hepatitis?",
        "reference": "In active hepatitis, avoid hepatotoxic drugs (isoniazid, rifampicin, pyrazinamide). Consider ethambutol + streptomycin for 2 months, then ethambutol + isoniazid for 7 months. Monitor LFTs weekly.",
        "channel": "Mobile App",
        "feature": "clinical_protocols"
    },
    {
        "question": "What is the protocol for managing a patient with severe acute malnutrition?",
        "reference": "Admit to stabilization center. Give therapeutic milk F75 for 2-3 days, then transition to F100. Monitor for refeeding syndrome. Give vitamin A, zinc, and folic acid. Antibiotics for all children with SAM.",
        "channel": "Mobile App",
        "feature": "clinical_protocols"
    },
    
    # Web Portal Channel (5 questions)
    {
        "question": "What are the updated COVID-19 management guidelines for immunocompromised patients?",
        "reference": "Priority use of nirmatrelvir-ritonavir (Paxlovid) within 5 days of symptom onset. Remdesivir alternatives. Avoid immunomodulators in active infection. Ensure up-to-date vaccination including boosters.",
        "channel": "Web Portal",
        "feature": "clinical_protocols"
    },
    {
        "question": "How should a diabetic patient with foot ulcer be assessed in primary care?",
        "reference": "Assess: Wagner classification (grade 0-5), neuropathy (monofilament), peripheral vascular disease (ABI), infection (culture, probe-to-bone). Refer if grade ≥3 or osteomyelitis suspected.",
        "channel": "Web Portal",
        "feature": "triage_advisor"
    },
    {
        "question": "What is the protocol for managing status epilepticus in a 60kg adult?",
        "reference": "Benzodiazepine: lorazepam 4mg IV or diazepam 10mg IV. If persistent, phenytoin 20mg/kg IV or levetiracetam 1g IV. Refractory: phenobarbital or midazolam infusion. Monitor ABC and treat underlying cause.",
        "channel": "Web Portal",
        "feature": "safety_protocols"
    },
    {
        "question": "What are the contraindications to thrombolytic therapy in acute ischemic stroke?",
        "reference": "Absolute: intracranial hemorrhage, subarachnoid hemorrhage, recent stroke (3 months), intracranial surgery (3 months), bleeding diathesis, uncontrolled HTN (>185/110). Relative: >80 years, NIHSS >25, extensive infarction.",
        "channel": "Web Portal",
        "feature": "safety_protocols"
    },
    {
        "question": "How should a patient with suspected deep vein thrombosis be managed?",
        "reference": "Clinical assessment with Wells score. If high probability, start LMWH and arrange duplex ultrasound. If intermediate, D-dimer testing. If low probability and negative D-dimer, no further investigation. Start warfarin bridge therapy.",
        "channel": "Web Portal",
        "feature": "clinical_protocols"
    }
]

def generate_evaluation_dataset():
    """Generate the full evaluation dataset CSV"""
    df = pd.DataFrame(CLINICAL_EVALUATION_DATA)
    df.to_csv("evaluation_dataset.csv", index=False)
    print(f"Generated {len(df)} evaluation questions")
    return df

if __name__ == "__main__":
    generate_evaluation_dataset()