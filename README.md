# Claims Data Dashboard

Simple Streamlit dashboard for exploring healthcare claims data.

## Project Structure

- `data/claim_data.csv` — raw source data
- `data/clean_claims.csv` — transformed/cleaned dataset used by dashboard
- `data_analysis/data_transformation.py` — data cleaning/transformation script
- `data_analysis/dashboard.py` — Streamlit analytics dashboard

## Setup

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the Dashboard

```bash
source venv/bin/activate
streamlit run data_analysis/dashboard.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Dashboard Features

- Sidebar filters:
	- Insurance Type
	- Claim Status
- KPI metrics:
	- Total Claims
	- Total Billed
	- Total Paid
- Visuals:
	- Claim Status Distribution
	- Denied Claims by Insurance Type
	- Billed vs Paid Amount by Insurance Type
- Tables:
	- Denial Rate by Procedure Code (`Denied Count`, `Total Claims`, `Denial Rate (%)`)
	- Provider-Level Claims Summary (`Number_of_Claims`, status breakdown, `Total_Billed`, `Total_Paid`)
	- Filtered Data Preview