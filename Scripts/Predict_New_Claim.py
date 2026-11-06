
import joblib
import pandas as pd

# Load our previously trained AI model
model = joblib.load("Models/Denial_Prediction_Model.pkl")

print("Saved AI model loaded successfully!")

# Details of our new insurance claim

new_claim = pd.DataFrame([
    {
        "Eligibility_Verified": 1,
        "Coding_Valid": 1,
        "Medical_Necessity_Met": 1,
        "Submission_Delay_Days": 2
    },
    {
        "Eligibility_Verified": 0,
        "Coding_Valid": 1,
        "Medical_Necessity_Met": 1,
        "Submission_Delay_Days": 15
    },
    {
        "Eligibility_Verified": 1,
        "Coding_Valid": 0,
        "Medical_Necessity_Met": 1,
        "Submission_Delay_Days": 10
    }
])


# Ask our saved AI to make a prediction
prediction = model.predict(new_claim)




denial_chances = model.predict_proba(new_claim)

for i in range(len(new_claim)):
    if prediction[i] == 1:
        print("Claim", i + 1, ": Likely Denied")
    else:
        print("Claim", i + 1, ": Likely Paid")

    chance = denial_chances[i][1] * 100
    print("Estimated Chance of Denial:", round(chance, 2), "%")
    print("--------------------")

print("Total claims analyzed:", len(new_claim))

