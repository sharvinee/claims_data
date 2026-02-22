import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import streamlit as st

DATA_PATH = "/workspaces/claims_data/data/clean_claims.csv"

st.set_page_config(page_title="Claims Dashboard", layout="wide")
st.title("Claims Dashboard")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["Date of Service"] = pd.to_datetime(data["Date of Service"], errors="coerce")
    return data


df = load_data(DATA_PATH)

st.sidebar.header("Filters")
insurance_options = sorted(df["Insurance Type"].dropna().unique().tolist())
status_options = sorted(df["Claim Status"].dropna().unique().tolist())

selected_insurance = st.sidebar.multiselect(
    "Insurance Type",
    options=insurance_options,
    default=insurance_options,
)
selected_status = st.sidebar.multiselect(
    "Claim Status",
    options=status_options,
    default=status_options,
)

filtered = df[
    df["Insurance Type"].isin(selected_insurance)
    & df["Claim Status"].isin(selected_status)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Total Claims", f"{len(filtered):,}")
col2.metric("Total Billed", f"${filtered['Billed Amount'].sum():,.0f}")
col3.metric("Total Paid", f"${filtered['Paid Amount'].sum():,.0f}")

st.subheader("Claim Status Distribution")
status_counts = filtered["Claim Status"].value_counts().reset_index()
status_counts.columns = ["Claim Status", "Count"]

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(data=status_counts, x="Claim Status", y="Count", hue="Claim Status", legend=False, palette="viridis", ax=ax1)
ax1.set_xlabel("Claim Status")
ax1.set_ylabel("Number of Claims")
plt.tight_layout()
st.pyplot(fig1)

st.subheader("Denied Claims by Insurance Type")
denials = filtered[filtered["Claim Status"] == "Denied"]
if denials.empty:
    st.info("No denied claims in the current filter selection.")
else:
    denial_counts = denials["Insurance Type"].value_counts().reset_index()
    denial_counts.columns = ["Insurance Type", "Denied Count"]

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=denial_counts, x="Insurance Type", y="Denied Count", hue="Insurance Type", legend=False, palette="magma", ax=ax2)
    ax2.set_xlabel("Insurance Type")
    ax2.set_ylabel("Denied Claims")
    plt.tight_layout()
    st.pyplot(fig2)

st.subheader("Diagnosis Codes with Highest Claims")
diagnosis_counts = (
    filtered["Diagnosis Code"]
    .dropna()
    .value_counts()
    .head(10)
    .reset_index()
)
diagnosis_counts.columns = ["Diagnosis Code", "Claim Count"]

if diagnosis_counts.empty:
    st.info("No diagnosis code data available in the current filter selection.")
else:
    fig_diag, ax_diag = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=diagnosis_counts,
        x="Diagnosis Code",
        y="Claim Count",
        hue="Diagnosis Code",
        order=diagnosis_counts["Diagnosis Code"],
        legend=False,
        palette="flare",
        ax=ax_diag,
    )
    ax_diag.set_xlabel("Diagnosis Code")
    ax_diag.set_ylabel("Number of Claims")
    ax_diag.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_diag.tick_params(axis="x")
    plt.tight_layout()
    st.pyplot(fig_diag)

st.subheader("Denial Rate by Procedure Code")
all_procedures = filtered["Procedure Code"].dropna()
if all_procedures.empty:
    st.info("No procedure code data available in the current filter selection.")
else:
    total_claims_by_procedure = (
        filtered.dropna(subset=["Procedure Code"])
        .groupby("Procedure Code")
        .size()
        .rename("Total Claims")
        .reset_index()
    )
    denied_counts_by_procedure = (
        denials.dropna(subset=["Procedure Code"])
        .groupby("Procedure Code")
        .size()
        .rename("Denied Count")
        .reset_index()
    )
    denial_rate_table = denied_counts_by_procedure.merge(
        total_claims_by_procedure,
        on="Procedure Code",
        how="right",
    )
    denial_rate_table["Denied Count"] = denial_rate_table["Denied Count"].fillna(0)
    denial_rate_table["Denied Count"] = denial_rate_table["Denied Count"].astype(int)
    denial_rate_table["Denial Rate (%)"] = (
        denial_rate_table["Denied Count"] / denial_rate_table["Total Claims"] * 100
    )
    denial_rate_table = denial_rate_table.sort_values(
        by=["Denial Rate (%)", "Denied Count"], ascending=[False, False]
    )

    st.markdown("**Denial Rate for All Procedures**")
    table_display = denial_rate_table.copy()
    table_display["Denial Rate (%)"] = table_display["Denial Rate (%)"].round(2)
    st.caption(f"Showing {len(table_display)} procedure codes.")
    st.dataframe(
        table_display[["Procedure Code", "Denied Count", "Total Claims", "Denial Rate (%)"]],
        use_container_width=True,
        hide_index=True,
        height=420,
    )

st.subheader("Billed vs Paid Amount by Insurance Type")
amounts = (
    filtered.groupby("Insurance Type")[["Billed Amount", "Paid Amount"]]
    .sum()
    .reset_index()
)
amounts_long = amounts.melt(
    id_vars="Insurance Type",
    value_vars=["Billed Amount", "Paid Amount"],
    var_name="Amount Type",
    value_name="Amount",
)

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(data=amounts_long, x="Insurance Type", y="Amount", hue="Amount Type", palette="Set2", ax=ax3)
ax3.set_xlabel("Insurance Type")
ax3.set_ylabel("Amount ($)")
plt.tight_layout()
st.pyplot(fig3)

st.subheader("Provider-Level Claims Summary")
provider_totals = (
    filtered.groupby("Provider ID")
    .agg(
        Number_of_Claims=("Claim ID", "count"),
        Total_Billed=("Billed Amount", "sum"),
        Total_Paid=("Paid Amount", "sum"),
    )
    .reset_index()
)

provider_status_counts = (
    filtered.pivot_table(
        index="Provider ID",
        columns="Claim Status",
        values="Claim ID",
        aggfunc="count",
        fill_value=0,
    )
    .reset_index()
)
provider_status_counts.columns = [
    "Provider ID" if col == "Provider ID" else f"Status_{col}"
    for col in provider_status_counts.columns
]

provider_summary = provider_totals.merge(
    provider_status_counts,
    on="Provider ID",
    how="left",
).sort_values(by="Number_of_Claims", ascending=False)

provider_summary["Provider ID"] = provider_summary["Provider ID"].astype(str)
provider_summary["Total_Billed"] = provider_summary["Total_Billed"].round(2)
provider_summary["Total_Paid"] = provider_summary["Total_Paid"].round(2)

st.dataframe(
    provider_summary,
    use_container_width=True,
    hide_index=True,
    height=420,
)

st.subheader("Data")
st.dataframe(df, use_container_width=True, height=420)
