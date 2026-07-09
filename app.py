from __future__ import annotations

from pathlib import Path
import math

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = BASE_DIR / "data" / "loans.csv"
RISK_STATUSES = ["Defaulted", "Overdue"]
HEALTHY_STATUSES = ["Active", "Closed"]


st.set_page_config(
    page_title="EduFin Portfolio",
    page_icon="EF",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_loans(uploaded_file=None) -> pd.DataFrame:
    source = uploaded_file if uploaded_file is not None else DEFAULT_DATA
    df = pd.read_csv(source)
    for col in ["application_date", "disbursement_date", "maturity_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d-%m-%Y", errors="coerce")
    return df


def inr_cr(value: float) -> str:
    return f"INR {value / 10_000_000:,.2f} Cr"


def inr_lakh(value: float) -> str:
    return f"INR {value / 100_000:,.2f} L"


def pct(value: float) -> str:
    return f"{value:,.2f}%"


def classify_health(default_rate: float) -> str:
    if default_rate > 15:
        return "CRITICAL"
    if default_rate > 10:
        return "HIGH RISK"
    if default_rate > 5:
        return "MODERATE RISK"
    return "HEALTHY"


def risk_color(status: str) -> str:
    return {
        "HEALTHY": "#15803d",
        "MODERATE RISK": "#ca8a04",
        "HIGH RISK": "#ea580c",
        "CRITICAL": "#b91c1c",
    }.get(status, "#334155")


def status_summary(df: pd.DataFrame) -> pd.DataFrame:
    total_amount = df["loan_amount"].sum()
    summary = (
        df.groupby("loan_status", dropna=False)
        .agg(
            loans=("loan_id", "count"),
            amount=("loan_amount", "sum"),
            avg_loan=("loan_amount", "mean"),
            avg_interest=("interest_rate", "mean"),
        )
        .reset_index()
    )
    summary["loan_pct"] = summary["loans"] / len(df) * 100
    summary["amount_pct"] = summary["amount"] / total_amount * 100
    summary["amount_cr"] = summary["amount"] / 10_000_000
    return summary.sort_values("loans", ascending=False)


def segment_summary(df: pd.DataFrame, segment: str) -> pd.DataFrame:
    grouped = (
        df.groupby(segment, dropna=False)
        .agg(
            loans=("loan_id", "count"),
            amount=("loan_amount", "sum"),
            defaulted=("loan_status", lambda s: (s == "Defaulted").sum()),
            overdue=("loan_status", lambda s: (s == "Overdue").sum()),
            avg_loan=("loan_amount", "mean"),
            avg_interest=("interest_rate", "mean"),
            avg_tenure=("loan_tenure_months", "mean"),
        )
        .reset_index()
    )
    grouped["at_risk"] = grouped["defaulted"] + grouped["overdue"]
    grouped["default_rate"] = grouped["defaulted"] / grouped["loans"] * 100
    grouped["risk_rate"] = grouped["at_risk"] / grouped["loans"] * 100
    grouped["amount_cr"] = grouped["amount"] / 10_000_000
    return grouped.sort_values("risk_rate", ascending=False)


def cohort_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = df.dropna(subset=["disbursement_date"]).copy()
    data["cohort_month"] = data["disbursement_date"].dt.to_period("M").astype(str)
    grouped = (
        data.groupby("cohort_month")
        .agg(
            loans=("loan_id", "count"),
            amount=("loan_amount", "sum"),
            defaulted=("loan_status", lambda s: (s == "Defaulted").sum()),
            overdue=("loan_status", lambda s: (s == "Overdue").sum()),
        )
        .reset_index()
        .sort_values("cohort_month")
    )
    grouped["at_risk"] = grouped["defaulted"] + grouped["overdue"]
    grouped["default_rate"] = grouped["defaulted"] / grouped["loans"] * 100
    grouped["risk_rate"] = grouped["at_risk"] / grouped["loans"] * 100
    grouped["amount_cr"] = grouped["amount"] / 10_000_000
    return grouped


def filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Controls")
    uploaded = st.sidebar.file_uploader("Upload EduFin CSV", type=["csv"])
    if uploaded is not None:
        df = load_loans(uploaded)

    statuses = sorted(df["loan_status"].dropna().unique().tolist())
    purposes = sorted(df["purpose_of_loan"].dropna().unique().tolist())
    tenures = sorted(df["loan_tenure_months"].dropna().unique().tolist())

    selected_statuses = st.sidebar.multiselect("Loan status", statuses, default=statuses)
    selected_purposes = st.sidebar.multiselect("Purpose", purposes, default=purposes)
    selected_tenures = st.sidebar.multiselect("Tenure months", tenures, default=tenures)

    min_amount = int(math.floor(df["loan_amount"].min()))
    max_amount = int(math.ceil(df["loan_amount"].max()))
    amount_range = st.sidebar.slider(
        "Loan amount",
        min_value=min_amount,
        max_value=max_amount,
        value=(min_amount, max_amount),
        step=10_000,
    )

    date_min = df["disbursement_date"].min().date()
    date_max = df["disbursement_date"].max().date()
    date_range = st.sidebar.date_input(
        "Disbursement period",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    mask = (
        df["loan_status"].isin(selected_statuses)
        & df["purpose_of_loan"].isin(selected_purposes)
        & df["loan_tenure_months"].isin(selected_tenures)
        & df["loan_amount"].between(amount_range[0], amount_range[1])
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["disbursement_date"].between(start, end)

    return df.loc[mask].copy()


raw_df = load_loans()
df = filtered_data(raw_df)

if df.empty:
    st.warning("No loans match the selected filters. Adjust the sidebar controls.")
    st.stop()

total_loans = len(df)
unique_customers = df["customer_id"].nunique()
unique_institutions = df["institution_id"].nunique()
total_amount = df["loan_amount"].sum()
defaulted = (df["loan_status"] == "Defaulted").sum()
overdue = (df["loan_status"] == "Overdue").sum()
at_risk = df["loan_status"].isin(RISK_STATUSES).sum()
default_rate = defaulted / total_loans * 100
risk_rate = at_risk / total_loans * 100
default_amount = df.loc[df["loan_status"] == "Defaulted", "loan_amount"].sum()
overdue_amount = df.loc[df["loan_status"] == "Overdue", "loan_amount"].sum()
risk_amount = default_amount + overdue_amount
health = classify_health(default_rate)

st.title("EduFin Portfolio Intelligence")
st.caption("Interactive loan portfolio, customer risk, and cohort analysis built from the EduFin notebooks and loans dataset.")

left, right = st.columns([0.72, 0.28], vertical_alignment="center")
with left:
    st.markdown(
        f"""
        <div style="padding:14px 18px;border-left:6px solid {risk_color(health)};background:#f8fafc;">
            <div style="font-size:0.85rem;color:#475569;">Executive health classification</div>
            <div style="font-size:1.8rem;font-weight:750;color:{risk_color(health)};">{health}</div>
            <div style="color:#475569;">Default rate {pct(default_rate)} and portfolio-at-risk rate {pct(risk_rate)} across the filtered book.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.download_button(
        "Download filtered data",
        df.to_csv(index=False).encode("utf-8"),
        "edufin_filtered_loans.csv",
        "text/csv",
        use_container_width=True,
    )

metric_cols = st.columns(6)
metric_cols[0].metric("Total loans", f"{total_loans:,}")
metric_cols[1].metric("Customers", f"{unique_customers:,}")
metric_cols[2].metric("Institutions", f"{unique_institutions:,}")
metric_cols[3].metric("Portfolio value", inr_cr(total_amount))
metric_cols[4].metric("Defaulted", f"{defaulted:,}", inr_cr(default_amount))
metric_cols[5].metric("At risk", f"{at_risk:,}", inr_cr(risk_amount))

tabs = st.tabs(
    [
        "Portfolio",
        "Risk Segments",
        "Cohorts",
        "Loan Explorer",
        "Scenario",
        "Notebook Facts",
    ]
)

with tabs[0]:
    st.subheader("Portfolio Health")
    summary = status_summary(df)

    chart_cols = st.columns(2)
    with chart_cols[0]:
        fig = px.pie(
            summary,
            names="loan_status",
            values="loans",
            hole=0.48,
            color="loan_status",
            color_discrete_map={
                "Active": "#2563eb",
                "Closed": "#16a34a",
                "Defaulted": "#dc2626",
                "Overdue": "#f59e0b",
            },
        )
        fig.update_layout(title="Loan Count by Status", legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    with chart_cols[1]:
        fig = px.bar(
            summary,
            x="loan_status",
            y="amount_cr",
            color="loan_status",
            text=summary["amount_cr"].map(lambda x: f"{x:.2f} Cr"),
            color_discrete_map={
                "Active": "#2563eb",
                "Closed": "#16a34a",
                "Defaulted": "#dc2626",
                "Overdue": "#f59e0b",
            },
        )
        fig.update_layout(title="Financial Exposure by Status", xaxis_title="", yaxis_title="INR Crores", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    formatted = summary.copy()
    formatted["amount"] = formatted["amount"].map(inr_cr)
    formatted["avg_loan"] = formatted["avg_loan"].map(inr_lakh)
    formatted["loan_pct"] = formatted["loan_pct"].map(pct)
    formatted["amount_pct"] = formatted["amount_pct"].map(pct)
    formatted["avg_interest"] = formatted["avg_interest"].map(pct)
    st.dataframe(
        formatted[["loan_status", "loans", "loan_pct", "amount", "amount_pct", "avg_loan", "avg_interest"]],
        use_container_width=True,
        hide_index=True,
    )

with tabs[1]:
    st.subheader("Risk Segmentation")
    segment = st.selectbox("Segment by", ["purpose_of_loan", "loan_tenure_months", "institution_id", "customer_id"])
    min_loans = st.slider("Minimum loans per segment", 1, 100, 20)
    seg = segment_summary(df, segment)
    seg = seg[seg["loans"] >= min_loans].copy()

    if seg.empty:
        st.info("No segments meet the minimum loan threshold.")
    else:
        top = seg.head(20)
        fig = px.bar(
            top.sort_values("risk_rate"),
            x="risk_rate",
            y=segment,
            orientation="h",
            color="default_rate",
            text=top.sort_values("risk_rate")["risk_rate"].map(lambda x: f"{x:.1f}%"),
            color_continuous_scale=["#16a34a", "#f59e0b", "#dc2626"],
        )
        fig.update_layout(title="Highest Risk Segments", xaxis_title="At-risk rate", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        display_seg = seg.copy()
        display_seg["amount"] = display_seg["amount"].map(inr_cr)
        display_seg["avg_loan"] = display_seg["avg_loan"].map(inr_lakh)
        for col in ["default_rate", "risk_rate", "avg_interest"]:
            display_seg[col] = display_seg[col].map(pct)
        st.dataframe(
            display_seg[
                [
                    segment,
                    "loans",
                    "amount",
                    "defaulted",
                    "overdue",
                    "default_rate",
                    "risk_rate",
                    "avg_loan",
                    "avg_interest",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

with tabs[2]:
    st.subheader("Disbursement Cohort Tracking")
    cohorts = cohort_summary(df)
    min_cohort_size = st.slider("Minimum loans per cohort", 1, 150, 30)
    cohorts_view = cohorts[cohorts["loans"] >= min_cohort_size].copy()

    fig = px.line(
        cohorts,
        x="cohort_month",
        y=["default_rate", "risk_rate"],
        markers=True,
        labels={"value": "Rate", "cohort_month": "Disbursement month", "variable": "Metric"},
    )
    fig.update_layout(title="Monthly Cohort Default and At-Risk Rates")
    st.plotly_chart(fig, use_container_width=True)

    if not cohorts_view.empty:
        risky = cohorts_view.sort_values("risk_rate", ascending=False).head(12)
        fig = px.bar(
            risky.sort_values("risk_rate"),
            x="risk_rate",
            y="cohort_month",
            orientation="h",
            color="default_rate",
            text=risky.sort_values("risk_rate")["risk_rate"].map(lambda x: f"{x:.1f}%"),
            color_continuous_scale=["#22c55e", "#f97316", "#b91c1c"],
        )
        fig.update_layout(title="Highest Risk Disbursement Cohorts", xaxis_title="At-risk rate", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    display_cohorts = cohorts_view.sort_values("risk_rate", ascending=False).copy()
    display_cohorts["amount"] = display_cohorts["amount"].map(inr_cr)
    for col in ["default_rate", "risk_rate"]:
        display_cohorts[col] = display_cohorts[col].map(pct)
    st.dataframe(display_cohorts, use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Loan Explorer")
    search = st.text_input("Search loan, customer, institution, status, or purpose")
    explorer = df.copy()
    if search:
        needle = search.lower()
        explorer = explorer[
            explorer.astype(str).apply(lambda row: row.str.lower().str.contains(needle, regex=False).any(), axis=1)
        ]
    st.dataframe(explorer.sort_values("loan_amount", ascending=False), use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Loss and Recovery Scenario")
    col_a, col_b, col_c = st.columns(3)
    recovery_rate = col_a.slider("Expected overdue recovery", 0, 100, 35)
    default_recovery = col_b.slider("Expected default recovery", 0, 100, 5)
    new_disbursement = col_c.number_input("Planned new disbursement in INR Cr", min_value=0.0, value=0.0, step=1.0)

    expected_loss = default_amount * (1 - default_recovery / 100) + overdue_amount * (1 - recovery_rate / 100)
    future_portfolio = total_amount + new_disbursement * 10_000_000
    expected_loss_rate = expected_loss / future_portfolio * 100 if future_portfolio else 0

    sc_cols = st.columns(4)
    sc_cols[0].metric("Default exposure", inr_cr(default_amount))
    sc_cols[1].metric("Overdue exposure", inr_cr(overdue_amount))
    sc_cols[2].metric("Expected loss", inr_cr(expected_loss))
    sc_cols[3].metric("Expected loss rate", pct(expected_loss_rate))

    st.info(
        "Scenario output is a planning estimate. It uses current defaulted and overdue balances only; the CSV does not include repayment transactions, collateral, collections, or probability-of-default model scores."
    )

with tabs[5]:
    st.subheader("Notebook Facts and Data Limits")
    st.markdown(
        """
        **Day 1: Portfolio Health** quantified status mix, scale, default rate, at-risk value, and an executive health class.

        **Day 2: Customer Risk Analysis** focused on who is driving risk through customer and segment level views.

        **Day 3: Crisis Timeline Analysis** investigated default velocity, cohort tracking, institutional risk, cumulative loss trajectory, and repayment seasonality.

        **Current CSV facts:** 5,000 loans, 3,000 customers, 3,183 institutions, INR 204.82 Cr total exposure, 590 defaulted loans, 273 overdue loans, and INR 35.18 Cr combined defaulted plus overdue exposure.

        **Important data limitation:** the provided `loans.csv` has application, disbursement, and maturity dates, but it does not include `default_date`, repayment transaction history, payment status, institution names, income, credit score, or collection outcome fields. The interface therefore computes portfolio health, segmentation, and disbursement cohorts directly, while timeline repayment behavior is documented as a data gap.
        """
    )
