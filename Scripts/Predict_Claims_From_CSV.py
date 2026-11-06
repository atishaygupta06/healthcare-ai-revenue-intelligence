
import pandas as pd
from pathlib import Path

# Find the main project folder automatically
project_folder = Path(__file__).resolve().parent.parent

# Locate the synthetic claims dataset
input_file = project_folder / "Data" / "claims_ai.csv"

claims = pd.read_csv(input_file)

print("CSV file loaded successfully!")
print("Total claims in file:", len(claims))

import joblib

# Locate the trained AI model
model_file = project_folder / "Models" / "Denial_Prediction_Model.pkl"

# Load the trained model
model = joblib.load(model_file)

print("Trained AI model loaded successfully!")

features = claims[[
    "Eligibility_Verified",
    "Coding_Valid",
    "Medical_Necessity_Met",
    "Submission_Delay_Days"
]]

print("AI input data prepared successfully!")
print("Total claims ready for prediction:", len(features))

predictions = model.predict(features)

print("AI predictions completed successfully!")
print("Total predictions made:", len(predictions))

paid_count = sum(predictions == 0)
denied_count = sum(predictions == 1)

print("Claims predicted as Paid:", paid_count)
print("Claims predicted as Denied:", denied_count)

claims["AI_Prediction"] = predictions

print(claims[["Claim_ID", "AI_Prediction"]].head())

claims["AI_Prediction_Label"] = claims["AI_Prediction"].map({
    0: "Likely Paid",
    1: "Likely Denied"
})

print(claims[["Claim_ID", "AI_Prediction_Label"]].head())

denial_chances = model.predict_proba(features)[:, 1]

claims["AI_Denial_Percentage"] = (denial_chances * 100).round(2)

print(claims[[
    "Claim_ID",
    "AI_Prediction_Label",
    "AI_Denial_Percentage"
]].head())

# Save predictions to the project's Data folder
output_file = project_folder / "Data" / "AI_Claims_Predictions.csv"

claims.to_csv(output_file, index=False)

print("AI prediction report saved successfully!")


saved_report = pd.read_csv(output_file)

print("Saved report loaded successfully!")
print("Total rows in saved report:", len(saved_report))
print("Total columns in saved report:", len(saved_report.columns))

