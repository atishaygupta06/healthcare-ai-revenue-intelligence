
import pandas as pd
import mysql.connector
from getpass import getpass
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
print("Healthcare AI program started successfully!")

# Ask for the MySQL password
password = getpass("Enter your MySQL password: ")

# Connect Python to our healthcare database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="healthcare_ai"
)

print("Successfully connected to MySQL!")

# Create a cursor to communicate with MySQL
cursor = connection.cursor()

# Ask MySQL for 5 healthcare claims

cursor.execute("""
    SELECT *
    FROM claims_ai
    WHERE Claim_Status IN ('Paid', 'Denied')
""")


# Collect the results
claims = cursor.fetchall()


# Display the table
# Get the column names from MySQL
column_names = [column[0] for column in cursor.description]

# Convert the claims into a table
df = pd.DataFrame(claims, columns=column_names)

# Display the table


print("Total finalized claims:", len(df))
print(df["Claim_Status"].value_counts())


# Convert claim status into numbers
df["Denied_Flag"] = df["Claim_Status"].map({"Paid": 0, "Denied": 1})

# Display the first 5 results
print(df[["Claim_Status", "Denied_Flag"]].head())


# Select the information used to make predictions
X = df[["Eligibility_Verified", "Coding_Valid", "Medical_Necessity_Met", "Submission_Delay_Days"]]

# Select what we want to predict
y = df["Denied_Flag"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training claims:", len(X_train))
print("Testing claims:", len(X_test))

# Create our AI model

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)


# Teach the model using our training claims
model.fit(X_train, y_train)

# Confirm training is complete
print("AI model trained successfully!")

# Ask the AI to predict the outcomes of unseen claims
predictions = model.predict(X_test)

# Display the first 10 predictions
print("AI predictions:", predictions[:10])

print("AI prediction counts:", pd.Series(predictions).value_counts())


print("Actual results: ", y_test.iloc[:10].values)

# Compare AI predictions with the real outcomes
accuracy = accuracy_score(y_test, predictions)

print("AI Accuracy:", round(accuracy * 100, 2), "%")

# Check how many actual denials our AI identified
recall = recall_score(y_test, predictions)

print("Denial Detection Rate:", round(recall * 100, 2), "%")

# Check how many denial warnings were correct
precision = precision_score(y_test, predictions)

print("Correct Denial Warnings:", round(precision * 100, 2), "%")

# Compare every prediction with the actual result
results = confusion_matrix(y_test, predictions)

print("Prediction results:")
print(results)

# Create a Decision Tree
tree_model = DecisionTreeClassifier(max_depth=5, random_state=42)

# Teach the Decision Tree using our training claims
tree_model.fit(X_train, y_train)

# Ask it to predict the test claims
tree_predictions = tree_model.predict(X_test)

print("Decision Tree trained successfully!")

print("Decision Tree Accuracy:", round(accuracy_score(y_test, tree_predictions) * 100, 2), "%")

print("Decision Tree Denial Detection:", round(recall_score(y_test, tree_predictions) * 100, 2), "%")

print("Decision Tree Correct Warnings:", round(precision_score(y_test, tree_predictions, zero_division=0) * 100, 2), "%")

# Create a team of 100 Decision Trees
forest_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

# Teach the Random Forest
forest_model.fit(X_train, y_train)

# Ask it to predict claim outcomes
forest_predictions = forest_model.predict(X_test)

print("Random Forest trained successfully!")

print("Random Forest Accuracy:", round(accuracy_score(y_test, forest_predictions) * 100, 2), "%")

print("Random Forest Denial Detection:", round(recall_score(y_test, forest_predictions) * 100, 2), "%")

print("Random Forest Correct Warnings:", round(precision_score(y_test, forest_predictions, zero_division=0) * 100, 2), "%")

# Show which information the AI relies on most
importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": forest_model.feature_importances_
})

print(importance.sort_values(by="Importance", ascending=False))

# Save our trained Logistic Regression model
joblib.dump(model, "Models/Denial_Prediction_Model.pkl")

print("AI model saved successfully!")

cursor.close()
# Close the connection when finished
connection.close()
