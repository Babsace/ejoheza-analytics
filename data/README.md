# Data Dictionary

All four CSV files represent synthetic data for the EjoHeza Long-Term Savings Scheme.

## members.csv
| Column | Type | Description |
|---|---|---|
| member_id | VARCHAR(10) | Unique member identifier (e.g. M00001) |
| age | INT | Member age in years |
| gender | VARCHAR(10) | Male / Female |
| region | VARCHAR(50) | Rwandan administrative region |
| enrollment_date | DATE | Date the member joined the scheme |
| segment | VARCHAR(50) | Employment segment (Private, Public, Informal, etc.) |

## contributions.csv
| Column | Type | Description |
|---|---|---|
| contribution_id | VARCHAR(10) | Unique contribution identifier |
| member_id | VARCHAR(10) | Foreign key → members.member_id |
| amount | DECIMAL(15,2) | Contribution amount in Rwandan Francs (RWF) |
| date | DATE | Date the contribution was recorded |

## accounts.csv
| Column | Type | Description |
|---|---|---|
| member_id | VARCHAR(10) | Foreign key → members.member_id (also PK) |
| reported_balance | DECIMAL(15,2) | Balance as reported in the account summary table |
| last_transaction_date | DATE | Date of the most recent transaction (NULL if never funded) |

## regions.csv
| Column | Type | Description |
|---|---|---|
| region | VARCHAR(50) | Region name (Primary Key, matches members.region) |
| population | INT | Total population of the region |
| gps_coordinates | VARCHAR(100) | Lat/Lng coordinates for mapping |

## Known Data Quality Issues
- `accounts.last_transaction_date` contains empty strings that must be converted to NULL before altering the column type to DATE (handled in `sql/ejoheza_db.sql`).
- ~14% of accounts have a `reported_balance` of 0 with no `last_transaction_date`, indicating unfunded registrations.
- 50 members show a >10% discrepancy between `reported_balance` and the sum of their `contributions` records.
