"""
Educational EHR Platform - Insurance & Billing Module
Streamlit Cloud Version - Ready for Deployment

Instructions:
1. Copy this entire code
2. Save as 'app.py' (exactly, no .txt extension)
3. Upload to GitHub along with requirements.txt
4. Deploy to Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Educational EHR Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .patient-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563eb;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .insurance-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.25rem 0.25rem 0 0;
        color: white;
    }
    .success-feedback {
        background: #f0fdf4;
        border: 2px solid #bbf7d0;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #166534;
        margin: 1rem 0;
    }
    .error-feedback {
        background: #fef2f2;
        border: 2px solid #fecaca;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #dc2626;
        margin: 1rem 0;
    }
    .info-box {
        background: #eff6ff;
        border: 2px solid #bfdbfe;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #1d4ed8;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for tracking progress
if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None
if 'completed_cases' not in st.session_state:
    st.session_state.completed_cases = set()
if 'case_progress' not in st.session_state:
    st.session_state.case_progress = {}
if 'student_stats' not in st.session_state:
    st.session_state.student_stats = {
        'completed': 0,
        'correct_answers': 0,
        'total_answers': 0
    }

# Patient Data - Based on CSV structure provided
PATIENTS = [
    {
        'id': 'patient-001',
        'name': 'John Smith',
        'age': 68, 'gender': 'Male', 'mrn': 'MR001',
        'insurance': {
            'primary': 'Medicare',
            'planType': 'Part A & B',
            'reimbursementModel': 'Fee-for-Service',
            'memberID': 'JS123456789',
            'partA_deductible': 1632, 'partA_met': 1632,
            'partB_deductible': 240, 'partB_met': 240,
            'coinsurance': 20
        },
        'claims': [
            {'date': '2024-07-01', 'service': 'Hospital Stay (3 days)', 'amount': 8500, 'paid': 6800, 'status': 'Paid via DRG'},
            {'date': '2024-07-15', 'service': 'Cardiology Follow-up', 'amount': 300, 'paid': 240, 'status': 'Part B - 80%'},
            {'date': '2024-08-01', 'service': 'Lab Work', 'amount': 150, 'paid': 120, 'status': 'Part B - 80%'}
        ],
        'diagnosis': ['Coronary Artery Disease', 'Type 2 Diabetes', 'Hypertension'],
        'medications': ['Metformin 500mg BID', 'Lisinopril 10mg daily', 'Atorvastatin 20mg']
    },
    {
        'id': 'patient-002',
        'name': 'Maria Garcia',
        'age': 45, 'gender': 'Female', 'mrn': 'MR002',
        'insurance': {
            'primary': 'Private - BlueCross',
            'planType': 'PPO',
            'reimbursementModel': 'Value-Based Payment',
            'memberID': 'MG987654321',
            'deductible': 2500, 'deductible_met': 1200,
            'copay': 30, 'coinsurance': 20,
            'out_of_pocket_max': 8000, 'oop_met': 2400
        },
        'claims': [
            {'date': '2024-06-20', 'service': 'MRI Brain w/ Contrast', 'amount': 2800, 'paid': 2240, 'status': 'Paid after deductible'},
            {'date': '2024-07-10', 'service': 'Rheumatology Consult', 'amount': 400, 'paid': 320, 'status': 'Coinsurance applied'},
            {'date': '2024-08-05', 'service': 'Humira Injection (monthly)', 'amount': 1200, 'paid': 960, 'status': 'Tier 3 specialty drug'}
        ],
        'diagnosis': ['Rheumatoid Arthritis', 'Chronic Pain Syndrome', 'Mild Depression'],
        'medications': ['Methotrexate 15mg weekly', 'Humira 40mg injection', 'Sertraline 50mg']
    },
    {
        'id': 'patient-003',
        'name': 'David Lee',
        'age': 32, 'gender': 'Male', 'mrn': 'MR003',
        'insurance': {
            'primary': 'Medicaid',
            'planType': 'Managed Care',
            'reimbursementModel': 'Capitation',
            'memberID': 'DL456789012',
            'mco': 'WellCare',
            'copay': 0, 'pcp': 'Dr. Sarah Johnson'
        },
        'claims': [
            {'date': '2024-07-20', 'service': 'Emergency Room Visit', 'amount': 2500, 'paid': 0, 'status': 'DENIED - Non-emergency'},
            {'date': '2024-07-25', 'service': 'PCP Visit (anxiety)', 'amount': 150, 'paid': 150, 'status': 'Paid - Appropriate care'},
            {'date': '2024-08-01', 'service': 'Generic Buspirone', 'amount': 25, 'paid': 25, 'status': 'Medicaid formulary'}
        ],
        'diagnosis': ['Generalized Anxiety Disorder', 'Asthma - Mild Persistent'],
        'medications': ['Buspirone 10mg BID', 'Albuterol HFA inhaler', 'Fluticasone nasal spray']
    },
    {
        'id': 'patient-004',
        'name': 'Sarah Williams',
        'age': 29, 'gender': 'Female', 'mrn': 'MR004',
        'insurance': {
            'primary': 'Kaiser Permanente HMO',
            'planType': 'HMO',
            'reimbursementModel': 'Capitation',
            'memberID': 'SW345678901',
            'pcp': 'Dr. Jennifer Adams',
            'copay': 25, 'specialist_copay': 40
        },
        'claims': [
            {'date': '2024-07-15', 'service': 'Prenatal Visit (28 weeks)', 'amount': 200, 'paid': 175, 'status': 'Copay applied'},
            {'date': '2024-07-22', 'service': 'Obstetric Ultrasound', 'amount': 350, 'paid': 310, 'status': 'In-network specialist'},
            {'date': '2024-08-01', 'service': 'Prenatal Labs', 'amount': 180, 'paid': 180, 'status': 'Pregnancy - 100% covered'}
        ],
        'diagnosis': ['Intrauterine Pregnancy - 30 weeks', 'Iron Deficiency Anemia', 'Pregnancy-induced hypertension'],
        'medications': ['Prenatal vitamins with Iron', 'Iron sulfate 325mg', 'Low-dose Aspirin 81mg']
    },
    {
        'id': 'patient-005',
        'name': 'Robert Johnson',
        'age': 55, 'gender': 'Male', 'mrn': 'MR005',
        'insurance': {
            'primary': 'Uninsured',
            'planType': 'Self-Pay',
            'reimbursementModel': 'Fee-for-Service',
            'charity_care': 'Approved - 80% discount',
            'payment_plan': '$100/month',
            'financial_counselor': 'Lisa Martinez, MSW'
        },
        'claims': [
            {'date': '2024-06-10', 'service': 'ER - Acute MI', 'amount': 12500, 'paid': 2500, 'status': 'Charity care - 80% discount'},
            {'date': '2024-06-11', 'service': 'Cardiac Catheterization', 'amount': 25000, 'paid': 5000, 'status': 'Charity care - 80% discount'},
            {'date': '2024-07-01', 'service': 'Cardiology Follow-up', 'amount': 300, 'paid': 60, 'status': 'Payment plan active'}
        ],
        'diagnosis': ['STEMI - Anterior wall (resolved)', 'Coronary Artery Disease', 'Hyperlipidemia', 'Tobacco Use Disorder'],
        'medications': ['Clopidogrel 75mg', 'Metoprolol 50mg BID', 'Atorvastatin 80mg', 'Nicotine patch']
    },
    {
        'id': 'patient-006',
        'name': 'Linda Chen',
        'age': 72, 'gender': 'Female', 'mrn': 'MR006',
        'insurance': {
            'primary': 'Humana Medicare Advantage',
            'planType': 'Medicare Advantage (Part C)',
            'reimbursementModel': 'Capitation',
            'memberID': 'LC234567890',
            'copay': 15, 'specialist_copay': 35,
            'part_d_included': True,
            'star_rating': '4 stars'
        },
        'claims': [
            {'date': '2024-07-08', 'service': 'Annual Wellness Visit', 'amount': 250, 'paid': 250, 'status': 'Preventive - 100%'},
            {'date': '2024-07-15', 'service': 'Screening Mammography', 'amount': 280, 'paid': 280, 'status': 'Preventive - 100%'},
            {'date': '2024-08-01', 'service': 'Prescription drugs (3-month)', 'amount': 450, 'paid': 385, 'status': 'Part D coverage'}
        ],
        'diagnosis': ['Osteoporosis', 'Essential Hypertension', 'Vitamin D Deficiency', 'Osteoarthritis - knees'],
        'medications': ['Alendronate 70mg weekly', 'Amlodipine 10mg', 'Vitamin D3 2000 IU', 'Acetaminophen 650mg PRN']
    },
    {
        'id': 'patient-007',
        'name': 'Michael Davis',
        'age': 41, 'gender': 'Male', 'mrn': 'MR007',
        'insurance': {
            'primary': 'Aetna High Deductible Health Plan',
            'planType': 'HDHP with HSA',
            'reimbursementModel': 'Value-Based Payment',
            'memberID': 'MD567890123',
            'deductible': 4000, 'deductible_met': 3800,
            'hsa_balance': 5500, 'coinsurance': 20,
            'out_of_pocket_max': 8000
        },
        'claims': [
            {'date': '2024-05-15', 'service': 'Laparoscopic Appendectomy', 'amount': 18000, 'paid': 14400, 'status': 'After deductible - 20% coinsurance'},
            {'date': '2024-06-01', 'service': 'Post-op surgical visit', 'amount': 250, 'paid': 200, 'status': '20% coinsurance'},
            {'date': '2024-08-01', 'service': 'HSA-eligible expenses', 'amount': 180, 'paid': 180, 'status': 'Paid with HSA funds'}
        ],
        'diagnosis': ['Post-operative status - appendectomy', 'Resolved acute appendicitis'],
        'medications': ['Ibuprofen 600mg PRN', 'Multivitamin daily']
    },
    {
        'id': 'patient-008',
        'name': 'Jennifer Brown',
        'age': 38, 'gender': 'Female', 'mrn': 'MR008',
        'insurance': {
            'primary': 'Tricare Prime',
            'planType': 'Military Health System',
            'reimbursementModel': 'Capitation',
            'memberID': 'JB890123456',
            'sponsor_status': 'Active Duty Spouse',
            'mtf': 'Naval Medical Center',
            'copay': 12
        },
        'claims': [
            {'date': '2024-07-12', 'service': 'Mental Health Initial Evaluation', 'amount': 250, 'paid': 238, 'status': 'Tricare Standard Rate'},
            {'date': '2024-07-26', 'service': 'Individual Psychotherapy (45 min)', 'amount': 150, 'paid': 138, 'status': 'Unlimited sessions covered'},
            {'date': '2024-08-09', 'service': 'Sertraline 100mg (90-day supply)', 'amount': 45, 'paid': 40, 'status': 'Military pharmacy discount'}
        ],
        'diagnosis': ['Major Depressive Disorder - Recurrent', 'Post-Traumatic Stress Disorder', 'Adjustment Disorder'],
        'medications': ['Sertraline 100mg daily', 'Trazodone 50mg HS PRN', 'Individual therapy sessions']
    },
    {
        'id': 'patient-009',
        'name': 'Thomas Wilson',
        'age': 63, 'gender': 'Male', 'mrn': 'MR009',
        'insurance': {
            'primary': 'United Healthcare PPO',
            'planType': 'Commercial PPO',
            'reimbursementModel': 'Fee-for-Service',
            'memberID': 'TW789012345',
            'deductible': 2000, 'deductible_met': 2000,
            'copay': 35, 'coinsurance': 15,
            'out_of_pocket_max': 7500, 'oop_met': 3800
        },
        'claims': [
            {'date': '2024-06-05', 'service': 'Screening Colonoscopy w/ polypectomy', 'amount': 2200, 'paid': 1870, 'status': 'Became diagnostic - 15% coinsurance'},
            {'date': '2024-07-10', 'service': 'GI Follow-up visit', 'amount': 280, 'paid': 245, 'status': 'Specialist copay + coinsurance'},
            {'date': '2024-08-01', 'service': 'Surveillance CT Abdomen/Pelvis', 'amount': 1500, 'paid': 1275, 'status': '15% coinsurance'}
        ],
        'diagnosis': ['Adenomatous colon polyps (removed)', 'GERD', 'Strong family history of colorectal cancer'],
        'medications': ['Omeprazole 40mg daily', 'Psyllium fiber supplement', 'Multivitamin with folate']
    },
    {
        'id': 'patient-010',
        'name': 'Amanda Rodriguez',
        'age': 26, 'gender': 'Female', 'mrn': 'MR010',
        'insurance': {
            'primary': 'Medicaid - Pregnancy Coverage',
            'planType': 'Medicaid Managed Care',
            'reimbursementModel': 'Capitation',
            'memberID': 'AR234567890',
            'mco': 'Molina Healthcare',
            'pregnancy_medicaid': True,
            'postpartum_coverage': '12 months'
        },
        'claims': [
            {'date': '2024-07-15', 'service': 'Prenatal visit (24 weeks)', 'amount': 180, 'paid': 180, 'status': 'Medicaid pregnancy - 100%'},
            {'date': '2024-07-22', 'service': 'Prenatal vitamins w/ iron', 'amount': 35, 'paid': 35, 'status': 'Medicaid formulary'},
            {'date': '2024-08-05', 'service': 'Routine prenatal ultrasound', 'amount': 300, 'paid': 300, 'status': 'Pregnancy benefit'}
        ],
        'diagnosis': ['Intrauterine pregnancy - 26 weeks', 'Mild anemia of pregnancy', 'Low socioeconomic status'],
        'medications': ['Prenatal vitamins with iron', 'Folic acid 400mcg', 'Iron sulfate 325mg']
    }
]

# Learning Cases - Interactive scenarios based on CSV cases
LEARNING_CASES = [
    {
        'id': 'case-001', 'patientId': 'patient-001',
        'title': 'Medicare Hospital DRG Payment',
        'objective': 'Understand how Medicare pays hospitals using DRG rates',
        'scenario': 'John Smith was hospitalized for 3 days. The hospital billed $8,500, but Medicare only paid $6,800 under DRG 194 (cardiac procedures).',
        'question': 'Why did Medicare pay only $6,800 instead of the full $8,500 billed by the hospital?',
        'options': [
            'Medicare Part A only covers 80% of all hospital charges',
            'Medicare pays hospitals a fixed DRG rate, not actual charges',
            'The patient had not met his Part A deductible yet',
            'The hospital was out of network for Medicare'
        ],
        'correct': 1,
        'explanation': 'Medicare Part A pays hospitals based on Diagnosis Related Groups (DRGs), which are predetermined fixed rates for specific conditions and procedures. The hospital receives the DRG rate regardless of what they actually bill, incentivizing efficient care.'
    },
    {
        'id': 'case-002', 'patientId': 'patient-002',
        'title': 'PPO Cost Calculation with Deductible',
        'objective': 'Calculate patient costs under PPO with deductible and coinsurance',
        'scenario': 'Maria needs an MRI costing $2,800. Her PPO has a $2,500 deductible with $1,200 already met, and 20% coinsurance after the deductible.',
        'question': 'How much will Maria pay out-of-pocket for this MRI?',
        'options': [
            '$1,300 remaining deductible + $300 coinsurance = $1,600',
            '$560 (20% coinsurance on the full amount)',
            '$1,300 (just the remaining deductible amount)',
            '$280 (20% coinsurance after her plan negotiated rate)'
        ],
        'correct': 0,
        'explanation': 'Maria must first pay the remaining $1,300 of her deductible ($2,500 - $1,200 = $1,300). Then she pays 20% coinsurance on the remaining $1,500 ($300). Total: $1,300 + $300 = $1,600.'
    },
    {
        'id': 'case-003', 'patientId': 'patient-003',
        'title': 'Medicaid Managed Care ER Denial',
        'objective': 'Understand appropriate use of emergency services under Medicaid managed care',
        'scenario': 'David went to the ER for anxiety symptoms. His Medicaid managed care plan denied the $2,500 claim, stating "non-emergency use - could have been treated by PCP."',
        'question': 'What should David have done differently to avoid this denial?',
        'options': [
            'Gone to his assigned Primary Care Physician first',
            'Called the managed care organization\'s nurse line',
            'Used urgent care for non-emergency symptoms',
            'All of the above are appropriate alternatives'
        ],
        'correct': 3,
        'explanation': 'Medicaid managed care plans expect appropriate utilization. For non-emergency conditions like anxiety without acute symptoms, patients should use their PCP, urgent care, or call the MCO\'s 24/7 nurse line for guidance before using costly ER services.'
    },
    {
        'id': 'case-004', 'patientId': 'patient-004',
        'title': 'HMO Referral Requirement',
        'objective': 'Learn about HMO care coordination and referral systems',
        'scenario': 'Sarah needs specialist care for pregnancy complications. Her Kaiser HMO requires a referral from her PCP before she can see the maternal-fetal medicine specialist.',
        'question': 'What happens if Sarah sees the specialist without getting a PCP referral first?',
        'options': [
            'She pays a higher copay but is still covered',
            'The visit will be denied and not covered at all',
            'She can get retroactive authorization within 48 hours',
            'Emergency pregnancy care is always covered regardless'
        ],
        'correct': 1,
        'explanation': 'HMO plans require prior authorization/referrals from the Primary Care Physician for specialist visits. Without proper referral, the claim will be denied completely. This care coordination model helps control costs and ensures appropriate utilization.'
    },
    {
        'id': 'case-005', 'patientId': 'patient-005',
        'title': 'Hospital Charity Care Program',
        'objective': 'Understand charity care eligibility and discount calculations',
        'scenario': 'Robert is uninsured and received an 80% charity care discount. His household income is 200% of the Federal Poverty Level.',
        'question': 'What primarily determines the percentage of charity care discount a patient receives?',
        'options': [
            'The patient\'s employment status and work history',
            'Household income as a percentage of Federal Poverty Level',
            'The total amount of the medical bills owed',
            'Whether the patient has applied for insurance before'
        ],
        'correct': 1,
        'explanation': 'Charity care discounts are primarily based on household income relative to the Federal Poverty Level (FPL). Patients at 100-200% FPL typically receive 75-100% discounts. This sliding scale ensures healthcare access for low-income patients while hospitals meet community benefit requirements.'
    },
    {
        'id': 'case-006', 'patientId': 'patient-006',
        'title': 'Medicare Advantage Preventive Benefits',
        'objective': 'Learn about preventive care coverage in Medicare Advantage plans',
        'scenario': 'Linda\'s Medicare Advantage plan covered her annual wellness visit and mammography at 100% with no copay.',
        'question': 'Why are these services covered at 100% with no cost-sharing?',
        'options': [
            'Linda has met her annual deductible for the year',
            'Medicare Advantage plans have no copays for any services',
            'Preventive services must be covered at 100% by federal law',
            'These were provided at a Veterans Affairs facility'
        ],
        'correct': 2,
        'explanation': 'Federal law requires Medicare Advantage plans to cover Medicare-approved preventive services (like wellness visits and screening mammograms) at 100% with no deductibles, copays, or coinsurance. This promotes early detection and preventive care.'
    },
    {
        'id': 'case-007', 'patientId': 'patient-007',
        'title': 'High-Deductible Health Plan with HSA',
        'objective': 'Understand the triple tax advantage of Health Savings Accounts',
        'scenario': 'Michael has a High-Deductible Health Plan with an HSA. He used $180 from his HSA to pay for eligible medical expenses.',
        'question': 'What is the "triple tax advantage" of using HSA funds for qualified medical expenses?',
        'options': [
            'Tax-deductible contributions, tax-free growth, tax-free withdrawals',
            'Lower income taxes, lower payroll taxes, lower state taxes',
            'Contributions, employer matching, and investment gains',
            'Federal deduction, state deduction, and FICA exemption'
        ],
        'correct': 0,
        'explanation': 'HSAs offer a unique triple tax advantage: 1) Contributions are tax-deductible, 2) Account growth/earnings are tax-free, and 3) Withdrawals for qualified medical expenses are tax-free. This makes HSAs powerful savings vehicles for healthcare costs.'
    },
    {
        'id': 'case-008', 'patientId': 'patient-008',
        'title': 'Tricare Mental Health Coverage',
        'objective': 'Learn about mental health parity in military health benefits',
        'scenario': 'Jennifer receives unlimited mental health therapy sessions through Tricare Prime with the same copay as medical visits.',
        'question': 'What federal law requires insurance plans to provide equal mental health coverage?',
        'options': [
            'The Affordable Care Act (ACA)',
            'The Mental Health Parity and Addiction Equity Act',
            'The Military Health Care Act',
            'The Veterans Access, Choice and Accountability Act'
        ],
        'correct': 1,
        'explanation': 'The Mental Health Parity and Addiction Equity Act requires group health plans to provide mental health and substance abuse benefits that are comparable to medical/surgical benefits, including equal copays, session limits, and coverage criteria.'
    },
    {
        'id': 'case-009', 'patientId': 'patient-009',
        'title': 'Screening vs. Diagnostic Colonoscopy',
        'objective': 'Understand how procedure classification affects coverage',
        'scenario': 'Thomas had a "screening" colonoscopy, but when polyps were found and removed, it became "diagnostic" and subject to his deductible and coinsurance.',
        'question': 'Why did the procedure change from preventive to diagnostic coverage?',
        'options': [
            'The doctor made an error in the initial authorization',
            'When polyps are removed, it becomes a therapeutic procedure',
            'Screening colonoscopies are only covered every 10 years',
            'The patient should have chosen a different provider'
        ],
        'correct': 1,
        'explanation': 'When a screening colonoscopy results in polyp removal or biopsy, it becomes a diagnostic/therapeutic procedure subject to deductibles and coinsurance. The intervention changes the nature from preventive screening to treatment, affecting coverage and cost-sharing.'
    },
    {
        'id': 'case-010', 'patientId': 'patient-010',
        'title': 'Medicaid Pregnancy Coverage Extension',
        'objective': 'Learn about postpartum Medicaid coverage duration',
        'scenario': 'Amanda qualified for Medicaid during pregnancy and wants to know how long her coverage will last after delivery.',
        'question': 'Under recent federal expansions, how long can pregnancy-related Medicaid coverage extend postpartum?',
        'options': [
            'Coverage ends immediately at hospital discharge',
            '60 days postpartum (traditional coverage)',
            '12 months postpartum (with state option to extend)',
            'Permanently, as long as income requirements are met'
        ],
        'correct': 2,
        'explanation': 'The American Rescue Plan Act allowed states to extend postpartum Medicaid coverage from 60 days to 12 months. This extended coverage helps ensure continuity of care for new mothers and addresses maternal mortality concerns during the crucial postpartum period.'
    },
    # Additional cases for comprehensive learning
    {
        'id': 'case-011', 'patientId': 'patient-001',
        'title': 'Medicare Part B Coinsurance',
        'objective': 'Calculate Medicare Part B patient responsibility',
        'scenario': 'John has a cardiology follow-up visit. The doctor charges $300, Medicare approves $240, and pays 80% after the Part B deductible is met.',
        'question': 'How much does John owe if the doctor accepts Medicare assignment?',
        'options': [
            '$48 (20% of the Medicare-approved amount)',
            '$60 (20% of the doctor\'s full charge)',
            '$108 ($60 balance billing + $48 coinsurance)',
            '$0 (Medicare pays everything after deductible)'
        ],
        'correct': 0,
        'explanation': 'When a provider accepts Medicare assignment, they agree to accept the Medicare-approved amount as full payment. John pays 20% coinsurance on the approved amount: $240 × 20% = $48. The provider cannot bill for the difference between their charge and Medicare\'s approved amount.'
    },
    {
        'id': 'case-012', 'patientId': 'patient-002',
        'title': 'Value-Based Payment Incentives',
        'objective': 'Understand how value-based contracts affect patient care',
        'scenario': 'Maria\'s rheumatologist participates in a value-based payment contract that rewards better patient outcomes and care coordination.',
        'question': 'How might value-based payment models improve Maria\'s care compared to traditional fee-for-service?',
        'options': [
            'More focus on preventive care and care coordination',
            'Higher reimbursement rates for expensive procedures',
            'Unlimited access to any specialist without referrals',
            'Lower copays for all services regardless of necessity'
        ],
        'correct': 0,
        'explanation': 'Value-based payment models incentivize providers to focus on patient outcomes rather than volume of services. This typically leads to better preventive care, care coordination, chronic disease management, and overall quality improvements while controlling costs.'
    },
    {
        'id': 'case-013', 'patientId': 'patient-003',
        'title': 'Medicaid Capitation Model',
        'objective': 'Learn how capitation affects healthcare delivery',
        'scenario': 'David\'s Medicaid managed care organization receives a fixed monthly payment per member to provide all his healthcare needs.',
        'question': 'What incentive does this capitation model create for the managed care organization?',
        'options': [
            'Provide as many services as possible to justify the payment',
            'Keep members healthy to minimize expensive treatments',
            'Focus only on emergency and urgent care services',
            'Increase premiums annually to cover rising costs'
        ],
        'correct': 1,
        'explanation': 'Under capitation, managed care organizations receive fixed monthly payments regardless of services used. This creates incentives to keep members healthy through preventive care, care coordination, and chronic disease management to avoid costly emergency interventions and hospitalizations.'
    },
    {
        'id': 'case-014', 'patientId': 'patient-007',
        'title': 'HSA Contribution Limits and Penalties',
        'objective': 'Learn HSA rules and tax implications',
        'scenario': 'Michael wants to maximize his HSA contributions. For 2024, the individual contribution limit is $4,150, but he\'s considering contributing $5,000.',
        'question': 'What happens if Michael contributes more than the annual HSA limit?',
        'options': [
            'The excess is automatically refunded by the bank',
            'He pays a 6% excise tax on excess contributions',
            'The contribution is treated as a regular investment',
            'There are no penalties for excess contributions'
        ],
        'correct': 1,
        'explanation': 'Excess HSA contributions are subject to a 6% excise tax each year until the excess amount (plus earnings) is withdrawn. The excess must be removed by the tax deadline to avoid ongoing penalties, making it important to stay within annual contribution limits.'
    },
    {
        'id': 'case-015', 'patientId': 'patient-006',
        'title': 'Medicare Advantage Star Ratings',
        'objective': 'Understand Medicare Advantage quality measures',
        'scenario': 'Linda chose her Medicare Advantage plan partly because it has a 4-star rating from Medicare.',
        'question': 'What do Medicare Advantage Star Ratings measure?',
        'options': [
            'Only customer satisfaction with the health plan',
            'Quality of care, member experience, and plan administration',
            'How much the plan saves compared to Original Medicare',
            'The number of providers in the plan\'s network'
        ],
        'correct': 1,
        'explanation': 'Medicare Advantage Star Ratings (1-5 stars) measure multiple aspects including quality of care, member experience, member complaints, customer service, and health plan administration. Higher ratings indicate better overall performance and may qualify plans for bonus payments from Medicare.'
    }
]

def get_plan_type_color(plan_type):
    """Return color for plan type badge"""
    colors = {
        'PPO': '#3b82f6', 'HMO': '#10b981', 'Part A & B': '#8b5cf6',
        'Medicare Advantage (Part C)': '#8b5cf6', 'Managed Care': '#f59e0b',
        'Medicaid Managed Care': '#f59e0b', 'Military Health System': '#ef4444',
        'Self-Pay': '#6b7280', 'HDHP with HSA': '#06b6d4', 'Commercial PPO': '#3b82f6'
    }
    return colors.get(plan_type, '#6b7280')

def get_reimbursement_color(model):
    """Return color for reimbursement model badge"""
    colors = {
        'Fee-for-Service': '#3b82f6',
        'Value-Based Payment': '#10b981',
        'Capitation': '#8b5cf6'
    }
    return colors.get(model, '#6b7280')

def calculate_completion_stats():
    """Calculate overall completion statistics"""
    total_cases = len(LEARNING_CASES)
    completed = len(st.session_state.completed_cases)
    accuracy = 0
    if st.session_state.student_stats['total_answers'] > 0:
        accuracy = (st.session_state.student_stats['correct_answers'] / 
                   st.session_state.student_stats['total_answers']) * 100
    return total_cases, completed, accuracy

def handle_case_answer(case_id, selected_option, correct_answer):
    """Handle student answer submission"""
    is_correct = selected_option == correct_answer
    
    # Update case progress
    st.session_state.case_progress[case_id] = {
        'completed': True,
        'correct': is_correct,
        'selected': selected_option
    }
    
    # Update completion tracking
    if case_id not in st.session_state.completed_cases:
        st.session_state.completed_cases.add(case_id)
        st.session_state.student_stats['completed'] += 1
    
    # Update answer statistics
    st.session_state.student_stats['total_answers'] += 1
    if is_correct:
        st.session_state.student_stats['correct_answers'] += 1

def render_learning_case(case):
    """Render an interactive learning case"""
    case_progress = st.session_state.case_progress.get(case['id'], {})
    is_completed = case_progress.get('completed', False)
    
    # Case header
    st.markdown(f"""
    <div class="info-box">
        <h4>{case['title']}</h4>
        <p><strong>Learning Objective:</strong> {case['objective']}</p>
        <p><strong>Scenario:</strong> {case['scenario']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Question:** {case['question']}")
    
    if is_completed:
        # Show completed case with results
        selected = case_progress.get('selected', -1)
        correct = case['correct']
        is_correct = case_progress.get('correct', False)
        
        # Display options with results
        for i, option in enumerate(case['options']):
            if i == correct:
                st.success(f"✅ **{chr(65+i)}.** {option}")
            elif i == selected and i != correct:
                st.error(f"❌ **{chr(65+i)}.** {option}")
            else:
                st.info(f"**{chr(65+i)}.** {option}")
        
        # Show explanation
        if is_correct:
            st.markdown(f"""
            <div class="success-feedback">
                <strong>🎉 Excellent! You got it right!</strong><br><br>
                <strong>Explanation:</strong> {case['explanation']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-feedback">
                <strong>📚 Learning Opportunity</strong><br><br>
                <strong>Explanation:</strong> {case['explanation']}
            </div>
            """, unsafe_allow_html=True)
            
    else:
        # Show interactive case
        selected_option = st.radio(
            "Choose your answer:",
            options=range(len(case['options'])),
            format_func=lambda x: f"**{chr(65+x)}.** {case['options'][x]}",
            key=f"case_{case['id']}"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Submit Answer", key=f"submit_{case['id']}", type="primary"):
                handle_case_answer(case['id'], selected_option, case['correct'])
                st.rerun()

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Educational EHR Platform</h1>
        <h2>Insurance & Billing Training Module</h2>
        <p>Interactive patient scenarios for healthcare finance education</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 Learning Dashboard")
        
        # Progress metrics
        total_cases, completed, accuracy = calculate_completion_stats()
        
        st.markdown("### 📊 Your Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cases Done", completed)
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col2:
            st.metric("Total Cases", total_cases)
            st.metric("Remaining", total_cases - completed)
        
        if total_cases > 0:
            progress = completed / total_cases
            st.progress(progress, f"Overall Progress: {progress:.1%}")
        
        st.divider()
        
        # Filters
        st.markdown("### 🔍 Find Patients")
        search_term = st.text_input("Search patients or insurance...")
        
        plan_types = sorted(list(set([p['insurance']['planType'] for p in PATIENTS])))
        selected_plan = st.selectbox("Filter by Plan Type", ["All Plans"] + plan_types)
        
        reimbursement_types = sorted(list(set([p['insurance']['reimbursementModel'] for p in PATIENTS])))
        selected_reimbursement = st.selectbox("Filter by Reimbursement", ["All Models"] + reimbursement_types)
        
        # Filter patients
        filtered_patients = PATIENTS
        if search_term:
            filtered_patients = [p for p in filtered_patients 
                               if search_term.lower() in p['name'].lower() or 
                                  search_term.lower() in p['insurance']['primary'].lower()]
        if selected_plan != "All Plans":
            filtered_patients = [p for p in filtered_patients if p['insurance']['planType'] == selected_plan]
        if selected_reimbursement != "All Models":
            filtered_patients = [p for p in filtered_patients if p['insurance']['reimbursementModel'] == selected_reimbursement]
        
        st.markdown(f"**{len(filtered_patients)} patients match your filters**")
    
    # Main content area
    if st.session_state.selected_patient is None:
        # Patient selection view
        st.markdown("## 👥 Select a Patient to Begin Learning")
        
        # Overview stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #2563eb;">10</h3>
                <p>Diverse Patients</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #10b981;">{total_cases}</h3>
                <p>Learning Cases</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #8b5cf6;">{completed}</h3>
                <p>Completed</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #f59e0b;">{accuracy:.1f}%</h3>
                <p>Accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Patient cards
        for patient in filtered_patients:
            patient_cases = [c for c in LEARNING_CASES if c['patientId'] == patient['id']]
            completed_cases = len([c for c in patient_cases if c['id'] in st.session_state.completed_cases])
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="patient-card">
                        <h3>{patient['name']} ({patient['age']}y {patient['gender']})</h3>
                        <p><strong>MRN:</strong> {patient['mrn']} | <strong>Insurance:</strong> {patient['insurance']['primary']}</p>
                        <div style="margin-top: 10px;">
                            <span class="insurance-badge" style="background-color: {get_plan_type_color(patient['insurance']['planType'])};">
                                {patient['insurance']['planType']}
                            </span>
                            <span class="insurance-badge" style="background-color: {get_reimbursement_color(patient['insurance']['reimbursementModel'])};">
                                {patient['insurance']['reimbursementModel']}
                            </span>
                        </div>
                        <p style="margin-top: 10px;"><strong>Learning Progress:</strong> {completed_cases}/{len(patient_cases)} cases completed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.write("")  # Spacing
                    st.write("")
                    if st.button(f"Explore Patient", key=f"select_{patient['id']}", type="primary"):
                        st.session_state.selected_patient = patient
                        st.rerun()
                    
                    if len(patient_cases) > 0:
                        progress = completed_cases / len(patient_cases)
                        st.progress(progress, f"{progress:.0%} Complete")
    
    else:
        # Patient detail view
        patient = st.session_state.selected_patient
        
        # Patient header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"# {patient['name']}")
            st.markdown(f"**{patient['mrn']}** • {patient['age']} years old • {patient['gender']}")
            
            # Insurance badges
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <span class="insurance-badge" style="background-color: {get_plan_type_color(patient['insurance']['planType'])};">
                    {patient['insurance']['planType']}
                </span>
                <span class="insurance-badge" style="background-color: {get_reimbursement_color(patient['insurance']['reimbursementModel'])};">
                    {patient['insurance']['reimbursementModel']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("← Back to Patients", type="secondary"):
                st.session_state.selected_patient = None
                st.rerun()
        
        # Tabs for patient information
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 Demographics", 
            "🏥 Insurance Details", 
            "💰 Claims & Billing", 
            "⚕️ Clinical Info", 
            "📚 Learning Cases"
        ])
        
        with tab1:
            st.markdown("### Patient Demographics")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Full Name:** {patient['name']}")
                st.markdown(f"**Age:** {patient['age']} years")
                st.markdown(f"**Gender:** {patient['gender']}")
            with col2:
                st.markdown(f"**Medical Record Number:** {patient['mrn']}")
                st.markdown(f"**Date of Birth:** [Protected Health Information]")
                st.markdown(f"**Address:** [Protected Health Information]")
        
        with tab2:
            st.markdown("### Insurance Coverage Details")
            insurance = patient['insurance']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Primary Insurance")
                st.markdown(f"**Carrier:** {insurance['primary']}")
                st.markdown(f"**Plan Type:** {insurance['planType']}")
                st.markdown(f"**Reimbursement Model:** {insurance['reimbursementModel']}")
                if 'memberID' in insurance:
                    st.markdown(f"**Member ID:** `{insurance['memberID']}`")
                
                # Special features
                if 'pcp' in insurance:
                    st.markdown(f"**Primary Care Provider:** {insurance['pcp']}")
                if 'mco' in insurance:
                    st.markdown(f"**Managed Care Organization:** {insurance['mco']}")
            
            with col2:
                st.markdown("#### Cost Sharing")
                if 'deductible' in insurance:
                    st.markdown(f"**Annual Deductible:** ${insurance['deductible']:,}")
                    if 'deductible_met' in insurance:
                        met = insurance['deductible_met']
                        remaining = insurance['deductible'] - met
                        st.markdown(f"**Deductible Met:** ${met:,}")
                        st.markdown(f"**Remaining:** ${remaining:,}")
                        progress = met / insurance['deductible']
                        st.progress(progress, f"Deductible Progress: {progress:.1%}")
                
                if 'copay' in insurance:
                    st.markdown(f"**Primary Care Copay:** ${insurance['copay']}")
                if 'specialist_copay' in insurance:
                    st.markdown(f"**Specialist Copay:** ${insurance['specialist_copay']}")
                if 'coinsurance' in insurance:
                    st.markdown(f"**Coinsurance:** {insurance['coinsurance']}%")
                
                if 'out_of_pocket_max' in insurance:
                    st.markdown(f"**Out-of-Pocket Maximum:** ${insurance['out_of_pocket_max']:,}")
                    if 'oop_met' in insurance:
                        met = insurance['oop_met']
                        st.markdown(f"**OOP Met:** ${met:,}")
                        progress = met / insurance['out_of_pocket_max']
                        st.progress(progress, f"OOP Progress: {progress:.1%}")
            
            # Special programs
            if 'charity_care' in insurance:
                st.success(f"🏥 **Charity Care Status:** {insurance['charity_care']}")
            if 'hsa_balance' in insurance:
                st.info(f"💰 **Health Savings Account:** ${insurance['hsa_balance']:,} available")
            if 'pregnancy_medicaid' in insurance and insurance['pregnancy_medicaid']:
                st.info(f"🤱 **Pregnancy Medicaid:** Extended coverage through {insurance.get('postpartum_coverage', 'delivery')}")
        
        with tab3:
            st.markdown("### Claims History & Billing")
            
            if patient['claims']:
                # Create claims dataframe
                claims_df = pd.DataFrame(patient['claims'])
                claims_df['patient_responsibility'] = claims_df['amount'] - claims_df['paid']
                
                # Claims table
                st.dataframe(
                    claims_df[['date', 'service', 'amount', 'paid', 'patient_responsibility', 'status']].rename(columns={
                        'date': 'Date',
                        'service': 'Service Description',
                        'amount': 'Billed Amount ($)',
                        'paid': 'Insurance Paid ($)',
                        'patient_responsibility': 'Patient Owes ($)',
                        'status': 'Claim Status'
                    }),
                    use_container_width=True
                )
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Billed", f"${claims_df['amount'].sum():,}")
                with col2:
                    st.metric("Insurance Paid", f"${claims_df['paid'].sum():,}")
                with col3:
                    st.metric("Patient Responsibility", f"${claims_df['patient_responsibility'].sum():,}")
                
                # Visualization
                fig = px.bar(
                    claims_df, 
                    x='service', 
                    y=['amount', 'paid'], 
                    title='Claims Overview: Billed vs Paid Amounts',
                    barmode='group',
                    color_discrete_map={'amount': '#ef4444', 'paid': '#10b981'}
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No claims data available for this patient.")
        
        with tab4:
            st.markdown("### Clinical Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Active Diagnoses")
                for i, dx in enumerate(patient['diagnosis'], 1):
                    st.markdown(f"{i}. {dx}")
                
            with col2:
                st.markdown("#### Current Medications")
                for i, med in enumerate(patient['medications'], 1):
                    st.markdown(f"{i}. {med}")
        
        with tab5:
            st.markdown("### Interactive Learning Cases")
            
            # Get patient-specific cases
            patient_cases = [c for c in LEARNING_CASES if c['patientId'] == patient['id']]
            
            if not patient_cases:
                st.info(f"No learning cases available for {patient['name']} yet. Check back soon!")
            else:
                # Progress summary
                completed_cases = [c for c in patient_cases if c['id'] in st.session_state.completed_cases]
                accuracy_cases = [c for c in completed_cases if st.session_state.case_progress[c['id']].get('correct', False)]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Cases", len(patient_cases))
                with col2:
                    st.metric("Completed", len(completed_cases))
                with col3:
                    case_accuracy = (len(accuracy_cases) / len(completed_cases) * 100) if completed_cases else 0
                    st.metric("Accuracy", f"{case_accuracy:.0f}%")
                
                if len(patient_cases) > 0:
                    progress = len(completed_cases) / len(patient_cases)
                    st.progress(progress, f"Case Completion: {progress:.1%}")
                
                st.divider()
                
                # Display cases
                for i, case in enumerate(patient_cases, 1):
                    is_completed = case['id'] in st.session_state.completed_cases
                    is_correct = (is_completed and 
                                st.session_state.case_progress[case['id']].get('correct', False))
                    
                    # Case status indicator
                    if is_completed:
                        status = "✅ Completed" if is_correct else "📚 Completed (Review)"
                        expanded = False
                    else:
                        status = "🔄 Available"
                        expanded = True
                    
                    with st.expander(f"Case {i}: {case['title']} - {status}", expanded=expanded):
                        render_learning_case(case)

if __name__ == "__main__":
    main()
