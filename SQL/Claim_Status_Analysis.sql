
SELECT
    COUNT(*) AS Total_Claims,
    SUM(Claim_Status = 'Paid') AS Paid_Claims,
    SUM(Claim_Status = 'Denied') AS Denied_Claims,
    SUM(Claim_Status = 'Pending') AS Pending_Claims
FROM healthcare_ai.claims_ai;
