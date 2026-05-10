# 🛡️ EjoHeza Long-Term Savings Scheme — Analytics Project

> **RSSB Senior Data Analyst Technical Assessment**  
> End-to-end analytics project covering SQL querying, Python behavioral insights, and a real-time Streamlit monitoring dashboard.

---

## 📋 Project Overview

Rwanda Social Security Board (RSSB) administers the **EjoHeza** voluntary long-term savings scheme targeting Rwandans in the informal sector. This project addresses three operational challenges:

| Challenge | Approach |
|---|---|
| Irregular saving patterns | SQL cohort analysis + Python trend plots |
| Account balance discrepancies | SQL balance mismatch flagging + data quality checks |
| Regional inactivity risks | SQL regional aggregation + Streamlit choropleth |

---

## 🗂️ Repository Structure

```
ejoheza-analytics/
│
├── data/                        # Raw CSV datasets (source of truth)
│   ├── members.csv              # Member demographics & enrollment info
│   ├── contributions.csv        # Historical contribution records
│   ├── accounts.csv             # Current balances & last activity dates
│   └── regions.csv              # Region metadata (population, GPS)
│
├── sql/
│   └── ejoheza_db.sql           # Full DB setup + analytical queries (A, B, C)
│
├── notebooks/
│   └── ejoheza_db.ipynb         # Python EDA: trends, DQ checks, summary tables
│
├── dashboard/
│   └── EjoHeza_dashboard.py     # Streamlit interactive dashboard
│
├── requirements.txt             # Python dependencies
├── .gitignore                   # Excludes credentials, cache, env files
└── README.md                    # This file
```

---

## 🗄️ Part 1 — SQL Analysis

### Setup

```sql
CREATE DATABASE IF NOT EXISTS ejoheza_db;
USE ejoheza_db;
-- Then import the four CSVs via MySQL Workbench Table Data Import Wizard
-- or use: LOAD DATA INFILE (see sql/ejoheza_db.sql for full schema)
```

### A. Irregular Savers
> Members with fewer than 3 contributions in the past 12 months

```sql
SELECT member_id, COUNT(contribution_id) AS total_contributions
FROM contributions
WHERE date >= DATE_SUB('2024-06-23', INTERVAL 12 MONTH)
GROUP BY member_id
HAVING total_contributions < 3;
```
**Insight:** ~325 members (≈33% of the base) qualify as irregular savers — a significant engagement gap requiring targeted outreach.

---

### B. Balance Mismatch
> Members where reported balance differs from actual contribution sum by >10%

```sql
SELECT a.member_id, a.reported_balance, SUM(c.amount) AS actual_sum
FROM accounts a
JOIN contributions c ON a.member_id = c.member_id
GROUP BY a.member_id, a.reported_balance
HAVING ABS(a.reported_balance - SUM(c.amount)) > (a.reported_balance * 0.10)
    OR (a.reported_balance = 0 AND SUM(c.amount) > 0);
```
**Insight:** 50 members have balance discrepancies >10%, indicating ledger reconciliation issues requiring immediate remediation.

---

### C. Regional Inactivity
> Regions where >30% of members haven't contributed in the last 6 months

```sql
SELECT region,
       COUNT(member_id) AS total_members,
       SUM(CASE WHEN last_contrib < DATE_SUB('2024-06-23', INTERVAL 6 MONTH)
                  OR last_contrib IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS inactivity_rate
FROM (
    SELECT m.member_id, m.region, MAX(c.date) AS last_contrib
    FROM members m
    LEFT JOIN contributions c ON m.member_id = c.member_id
    GROUP BY m.member_id, m.region
) AS member_activity
GROUP BY region
HAVING inactivity_rate > 0.30;
```
**Insight:** No region currently exceeds the 30% threshold, but the Northern region (22.4%) shows the highest risk and warrants proactive outreach.

---

## 🐍 Part 2 — Python Behavioral Analysis

Run the notebook:

```bash
cd notebooks/
jupyter notebook ejoheza_db.ipynb
```

### What the notebook covers

1. **Monthly Contribution Trends** — line chart of total savings velocity over time
2. **Data Quality Check** — null counts, zero-balance accounts with no activity
3. **Demographic Summary Table** — contribution frequency by age group × gender

### Key Insights (100–150 words)

The monthly contribution trend reveals a consistent upward trajectory with seasonal dips in Q1, suggesting members align saving behavior with income cycles. The 25–45 age group drives the majority of contributions, with female members in the 35–45 bracket showing the highest saving frequency — a valuable segment for retention campaigns. Data quality checks uncovered accounts with a reported balance of zero but active contribution records, pointing to a synchronization lag between the transactions ledger and the account summary table. Approximately 14% of members have missing `last_transaction_date` values in the accounts table, reinforcing the need for a nightly reconciliation job. These findings suggest that targeted digital nudges for irregular savers and a backend data pipeline fix would meaningfully improve scheme health.

---

## 📊 Part 3 — Streamlit Dashboard

### Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ejoheza-analytics.git
cd ejoheza-analytics

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your MySQL credentials in dashboard/EjoHeza_dashboard.py
#    Edit the get_connection() function with your host/user/password

# 5. Run the dashboard
streamlit run dashboard/EjoHeza_dashboard.py
```

### Dashboard Pages

| Page | Content |
|---|---|
| **Executive Summary** | KPI cards (members, fund value, alerts) + monthly trend line + demographics bar chart |
| **Data Quality** | Flagged accounts with balance discrepancies >10% |
| **Regional Analysis** | Inactivity rate by region with heatmap coloring |

---

## ⚙️ Requirements

```
streamlit
pandas
mysql-connector-python
plotly
```

Install with: `pip install -r requirements.txt`

**MySQL:** Version 8.0+ recommended. Ensure `SET SQL_SAFE_UPDATES = 0` is run before date conversions (see `sql/ejoheza_db.sql`).

---

## 🔒 Security Note

Database credentials are **not** committed to this repository. Before running, update `dashboard/EjoHeza_dashboard.py`:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="YOUR_USERNAME",
        password="YOUR_PASSWORD",   # ← never commit real passwords
        database="ejoheza_db"
    )
```

For production deployments, use environment variables or a `.env` file (already excluded in `.gitignore`).

---

## 👤 Author

Prepared for the RSSB Senior Data Analyst technical assessment.
