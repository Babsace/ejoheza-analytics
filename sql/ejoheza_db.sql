show databases;

CREATE DATABASE IF NOT EXISTS ejoheza_db;
USE ejoheza_db;

-- 1. Regions Table
CREATE TABLE regions (
    region VARCHAR(50) PRIMARY KEY,
    population INT,
    gps_coordinates VARCHAR(100)
);

-- 2. Members Table
CREATE TABLE members (
    member_id VARCHAR(10) PRIMARY KEY,
    age INT,
    gender VARCHAR(10),
    region VARCHAR(50),
    enrollment_date DATE,
    segment VARCHAR(50),
    FOREIGN KEY (region) REFERENCES regions(region)
);

-- 3. Contributions Table
CREATE TABLE contributions (
    contribution_id VARCHAR(10) PRIMARY KEY,
    member_id VARCHAR(10),
    amount DECIMAL(15, 2),
    date DATE,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- 4. Accounts Table
CREATE TABLE accounts (
    member_id VARCHAR(10) PRIMARY KEY,
    reported_balance DECIMAL(15, 2),
    last_transaction_date VARCHAR (50),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

SHOW tables;

-- Confirming the imported datas (regions, members, contributions, accounts)

SELECT * FROM regions;
SELECT COUNT(*) AS regions_count
FROM regions;

SELECT * FROM members;
SELECT COUNT(*) AS members_count
FROM members;

SELECT * FROM contributions;
SELECT COUNT(*) AS contributions_count
FROM contributions;

SELECT * FROM accounts;

SELECT COUNT(*) AS accounts_count
FROM accounts;

SET SQL_SAFE_UPDATES = 0;
UPDATE accounts
SET last_transaction_date = STR_TO_DATE(last_transaction_date, '%Y-%m-%d');

-- Convert empty strings to NULL
UPDATE accounts 
SET last_transaction_date = NULL 
WHERE last_transaction_date = '' OR last_transaction_date = ' ';

-- Convert the valid strings to Date format
UPDATE accounts 
SET last_transaction_date = STR_TO_DATE(last_transaction_date, '%Y-%m-%d')
WHERE last_transaction_date IS NOT NULL;

-- Change the column type to DATE
ALTER TABLE accounts 
MODIFY last_transaction_date DATE;

-- A. Irregular Savers: Identify members who made fewer than 3 contributions in the past 12 months.
SELECT member_id, COUNT(contribution_id) as total_contributions
FROM contributions
WHERE date >= DATE_SUB('2024-06-23', INTERVAL 12 MONTH)
GROUP BY member_id
HAVING total_contributions < 3;

-- Interpretation: 325 members (approx. 33% of the base) are "Irregular Savers." This highlights a significant engagement gap where a third of the members are not meeting the expected saving frequency for long-term retirement security.

-- B. Balance Mismatch: Flag members where total contributions differ from reported balance by more than 10%.
SELECT a.member_id, a.reported_balance, SUM(c.amount) as actual_sum
FROM accounts a
JOIN contributions c ON a.member_id = c.member_id
GROUP BY a.member_id, a.reported_balance
HAVING ABS(a.reported_balance - SUM(c.amount)) > (a.reported_balance * 0.10)
   OR (a.reported_balance = 0 AND SUM(c.amount) > 0);
   
-- Interpretation: 50 members have a balance discrepancy greater than 10%. This points to technical inconsistencies between the transaction ledger and the account summary table, requiring immediate reconciliation to maintain member trust.
   
-- C. Regional Inactivity: List regions where over 30% of members haven’t contributed in the last 6 months.
SELECT region, 
       COUNT(member_id) as total_members,
       SUM(CASE WHEN last_contrib < DATE_SUB('2024-06-23', INTERVAL 6 MONTH) OR last_contrib IS NULL THEN 1 ELSE 0 END) / COUNT(*) as inactivity_rate
FROM (
    SELECT m.member_id, m.region, MAX(c.date) as last_contrib
    FROM members m
    LEFT JOIN contributions c ON m.member_id = c.member_id
    GROUP BY m.member_id, m.region
) as member_activity
GROUP BY region
HAVING inactivity_rate > 0.30;

-- Interpretation: No regions currently exceed the 30% threshold. However, the Northern region (22.4%) shows the highest risk of inactivity, suggesting that outreach efforts should prioritize this area to prevent further dropout.