
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

num_claims = 100000
claims = []

payers = ["Aetna", "Cigna", "UHC", "BCBS"]
cpt_codes = ["99213", "99214", "93000", "80053"]
icd_codes = ["E11.9", "I10", "J06.9", "M54.5"]

payer_risk = {
    "Aetna": 0.04,
    "Cigna": 0.02,
    "UHC": 0.05,
    "BCBS": 0.03
}

for i in range(num_claims):

    service_date = datetime(2025, 1, 1) + timedelta(
        days=random.randint(0, 364)
    )

    submission_delay = random.randint(1, 30)

    submission_date = service_date + timedelta(
        days=submission_delay
    )

    payer = random.choice(payers)
    cpt = random.choice(cpt_codes)
    icd = random.choice(icd_codes)

    billed = round(random.uniform(100, 10000), 2)
    allowed = round(billed * random.uniform(0.5, 0.9), 2)

    eligibility_verified = random.random() < 0.94

    authorization_required = cpt in ["99214", "93000"]

    authorization_approved = (
        random.random() < 0.92
        if authorization_required else True
    )

    coding_valid = random.random() < 0.95

    medical_necessity_met = random.random() < 0.93

    # Illustrative synthetic risk model.
    # These weights are NOT real insurer rules.
    denial_probability = 0.02 + payer_risk[payer]

    if not eligibility_verified:
        denial_probability += 0.45

    if authorization_required and not authorization_approved:
        denial_probability += 0.55

    if not coding_valid:
        denial_probability += 0.50

    if not medical_necessity_met:
        denial_probability += 0.40

    if submission_delay > 20:
        denial_probability += 0.08

    denial_probability = min(denial_probability, 0.95)

    # Pending is assigned separately from finalized outcomes.
    if random.random() < 0.10:
        status = "Pending"
    elif random.random() < denial_probability:
        status = "Denied"
    else:
        status = "Paid"

    paid = allowed if status == "Paid" else 0

    denial_code = ""

    if status == "Denied":
        if not coding_valid:
            denial_code = "CO-16"
        elif not medical_necessity_met:
            denial_code = "CO-50"
        elif authorization_required and not authorization_approved:
            denial_code = "CO-197"
        elif not eligibility_verified:
            denial_code = "ELIGIBILITY"
        else:
            denial_code = "OTHER"

    claims.append({
        "Claim_ID": f"CLM{i+1:06d}",
        "Patient_ID": f"PAT{random.randint(1, 20000):05d}",
        "Provider_ID": f"PRV{random.randint(1, 500):04d}",
        "Payer_ID": payer,
        "Service_Date": service_date.strftime("%Y-%m-%d"),
        "Submission_Date": submission_date.strftime("%Y-%m-%d"),
        "CPT_Code": cpt,
        "ICD_Code": icd,
        "Billed_Amount": billed,
        "Allowed_Amount": allowed,
        "Paid_Amount": paid,
        "Eligibility_Verified": int(eligibility_verified),
        "Authorization_Required": int(authorization_required),
        "Authorization_Approved": int(authorization_approved),
        "Coding_Valid": int(coding_valid),
        "Medical_Necessity_Met": int(medical_necessity_met),
        "Submission_Delay_Days": submission_delay,
        "Claim_Status": status,
        "Denial_Code": denial_code
    })

df = pd.DataFrame(claims)

project_folder = Path(__file__).resolve().parent.parent
output_file = project_folder / "Data" / "claims_ai.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("AI healthcare dataset generated successfully!")
print("Total claims:", len(df))
print("Saved to:", output_file)

print("\nClaim status distribution:")
print(df["Claim_Status"].value_counts())

print("\nDenial rate by eligibility:")
print(
    df.groupby("Eligibility_Verified")["Claim_Status"]
    .apply(lambda x: round((x == "Denied").mean() * 100, 2))
)

print("\n--- AI RISK FACTOR VALIDATION ---")

risk_factors = [
    "Eligibility_Verified",
    "Authorization_Approved",
    "Coding_Valid",
    "Medical_Necessity_Met"
]

finalized = df[
    df["Claim_Status"].isin(["Paid", "Denied"])
].copy()

for factor in risk_factors:
    print(f"\n{factor}")

    result = finalized.groupby(factor)["Claim_Status"].agg(
        Total_Claims="count",
        Denial_Rate=lambda x: round(
            (x == "Denied").mean() * 100, 2
        )
    )

    print(result)

print("\nSubmission delay analysis:")

finalized["Delay_Group"] = pd.cut(
    finalized["Submission_Delay_Days"],
    bins=[0, 10, 20, 30],
    labels=["1-10 Days", "11-20 Days", "21-30 Days"]
)

print(
    finalized.groupby(
        "Delay_Group", observed=True
    )["Claim_Status"].agg(
        Total_Claims="count",
        Denial_Rate=lambda x: round(
            (x == "Denied").mean() * 100, 2
        )
    )
)

