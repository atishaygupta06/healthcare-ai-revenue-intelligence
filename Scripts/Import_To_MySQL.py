
import csv
from pathlib import Path
from getpass import getpass
import mysql.connector

# Locate the NEW AI dataset
project_folder = Path(__file__).resolve().parent.parent
csv_file = project_folder / "Data" / "claims_ai.csv"

# Connect to the existing MySQL database
password = getpass("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="healthcare_ai"
)

cursor = connection.cursor()

# Insert data into the NEW claims_ai table
insert_query = """
INSERT INTO claims_ai (
    Claim_ID,
    Patient_ID,
    Provider_ID,
    Payer_ID,
    Service_Date,
    Submission_Date,
    CPT_Code,
    ICD_Code,
    Billed_Amount,
    Allowed_Amount,
    Paid_Amount,
    Eligibility_Verified,
    Authorization_Required,
    Authorization_Approved,
    Coding_Valid,
    Medical_Necessity_Met,
    Submission_Delay_Days,
    Claim_Status,
    Denial_Code
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s
)
"""

batch = []
total = 0

try:
    # Prevent duplicate imports
    cursor.execute("SELECT COUNT(*) FROM claims_ai")
    existing = cursor.fetchone()[0]

    if existing != 0:
        raise ValueError(
            f"Import stopped: claims_ai already contains "
            f"{existing:,} records."
        )

    with open(
        csv_file,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        columns = [
            "Claim_ID",
            "Patient_ID",
            "Provider_ID",
            "Payer_ID",
            "Service_Date",
            "Submission_Date",
            "CPT_Code",
            "ICD_Code",
            "Billed_Amount",
            "Allowed_Amount",
            "Paid_Amount",
            "Eligibility_Verified",
            "Authorization_Required",
            "Authorization_Approved",
            "Coding_Valid",
            "Medical_Necessity_Met",
            "Submission_Delay_Days",
            "Claim_Status",
            "Denial_Code"
        ]

        for row in reader:
            values = tuple(
                row[column] or None
                for column in columns
            )

            batch.append(values)

            # Import 1,000 records at a time
            if len(batch) == 1000:
                cursor.executemany(insert_query, batch)
                connection.commit()

                total += len(batch)
                print(f"Imported {total:,} claims")
                batch.clear()

        if batch:
            cursor.executemany(insert_query, batch)
            connection.commit()
            total += len(batch)

    print("\nAI dataset import completed!")
    print(f"Total claims imported: {total:,}")

finally:
    cursor.close()
    connection.close()
