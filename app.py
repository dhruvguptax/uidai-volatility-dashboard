import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("UIDAI Demographic Volatility Monitoring Platform")

# Load data
df = pd.read_csv("api_data_aadhar_demographic_0_500000.csv")
df["date"] = pd.to_datetime(df["date"], dayfirst=True)

# Reshape
long_df = df.melt(
    id_vars=["date", "state", "district", "pincode"],
    value_vars=["demo_age_5_17", "demo_age_17_"],
    var_name="age_group",
    value_name="update_count"
)

# Aggregate
monthly = long_df.groupby(
    ["state", "district", "age_group", pd.Grouper(key="date", freq="M")]
)["update_count"].sum().reset_index()

monthly["rolling_mean"] = monthly.groupby(
    ["state", "district", "age_group"]
)["update_count"].transform(lambda x: x.rolling(3).mean())

monthly["rolling_std"] = monthly.groupby(
    ["state", "district", "age_group"]
)["update_count"].transform(lambda x: x.rolling(3).std())

monthly["volatility_score"] = monthly["rolling_std"] / monthly["rolling_mean"]
monthly = monthly.dropna()

def classify(v):
    if v < 0.2:
        return "Stable"
    elif v < 0.5:
        return "Monitor"
    else:
        return "Immediate Attention"

monthly["risk_flag"] = monthly["volatility_score"].apply(classify)

latest = monthly.sort_values("date").groupby(
    ["state", "district", "age_group"]
).tail(1)

# KPI Row
st.subheader("National Risk Snapshot")
col1, col2, col3 = st.columns(3)

state_risk = latest.groupby("state")["volatility_score"].mean().reset_index()
state_risk["risk_flag"] = state_risk["volatility_score"].apply(classify)

col1.metric("Total States", state_risk.shape[0])
col2.metric("High Risk States", (state_risk["risk_flag"]=="Immediate Attention").sum())
col3.metric("States to Monitor", (state_risk["risk_flag"]=="Monitor").sum())

# Charts
st.subheader("State-Level Volatility")
fig1 = px.bar(state_risk, x="state", y="volatility_score", color="risk_flag")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Age Group Comparison")
age_summary = latest.groupby(["state","age_group"])["volatility_score"].mean().reset_index()
fig2 = px.bar(age_summary, x="state", y="volatility_score", color="age_group")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("National Trend")
trend = monthly.groupby("date")["volatility_score"].mean().reset_index()
fig3 = px.line(trend, x="date", y="volatility_score")
st.plotly_chart(fig3, use_container_width=True)

