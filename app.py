import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="UIDAI Demographic Volatility Platform",
    layout="wide"
)

st.title("UIDAI Demographic Volatility Monitoring Platform")
st.caption(
    "Early-warning signals for demographic stress using aggregated Aadhaar update data"
)


df = pd.read_csv("api_data_aadhar_demographic_0_500000.csv")
df["date"] = pd.to_datetime(df["date"], dayfirst=True)


long_df = df.melt(
    id_vars=["date", "state", "district", "pincode"],
    value_vars=["demo_age_5_17", "demo_age_17_"],
    var_name="age_group",
    value_name="update_count"
)


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


state_risk = latest.groupby("state")["volatility_score"].mean().reset_index()
state_risk["risk_flag"] = state_risk["volatility_score"].apply(classify)


state_coords = {
    "Andhra Pradesh": (15.91, 79.74),
    "Assam": (26.20, 92.94),
    "Bihar": (25.09, 85.31),
    "Chhattisgarh": (21.27, 81.86),
    "Delhi": (28.70, 77.10),
    "Gujarat": (22.25, 71.19),
    "Haryana": (29.06, 76.08),
    "Karnataka": (15.32, 75.71),
    "Kerala": (10.85, 76.27),
    "Madhya Pradesh": (22.97, 78.65),
    "Maharashtra": (19.75, 75.71),
    "Odisha": (20.95, 85.10),
    "Punjab": (31.14, 75.34),
    "Rajasthan": (27.02, 74.22),
    "Tamil Nadu": (11.12, 78.66),
    "Telangana": (18.11, 79.01),
    "Uttar Pradesh": (26.85, 80.91),
    "West Bengal": (22.99, 87.85)
}

state_risk["lat"] = state_risk["state"].apply(
    lambda x: state_coords.get(x, (None, None))[0]
)
state_risk["lon"] = state_risk["state"].apply(
    lambda x: state_coords.get(x, (None, None))[1]
)

state_risk = state_risk.dropna(subset=["lat", "lon"])


st.subheader("National Risk Snapshot")

col1, col2, col3 = st.columns(3)

col1.metric("Total States", state_risk.shape[0])
col2.metric(
    "High Risk States",
    (state_risk["risk_flag"] == "Immediate Attention").sum()
)
col3.metric(
    "States to Monitor",
    (state_risk["risk_flag"] == "Monitor").sum()
)


st.subheader("India Demographic Risk Map")

fig_map = px.scatter_geo(
    state_risk,
    lat="lat",
    lon="lon",
    color="risk_flag",
    size="volatility_score",
    hover_name="state",
    projection="natural earth"
)

fig_map.update_geos(
    scope="asia",
    center=dict(lat=22.5, lon=78.9),
    projection_scale=4,
    showcountries=True,
    countrycolor="LightGray"
)

st.plotly_chart(fig_map, use_container_width=True)

st.subheader("State-Level Demographic Volatility")

fig_state = px.bar(
    state_risk.sort_values("volatility_score", ascending=False),
    x="state",
    y="volatility_score",
    color="risk_flag"
)

st.plotly_chart(fig_state, use_container_width=True)


st.subheader("Age Group Comparison")

age_summary = latest.groupby(
    ["state", "age_group"]
)["volatility_score"].mean().reset_index()

fig_age = px.bar(
    age_summary,
    x="state",
    y="volatility_score",
    color="age_group"
)

st.plotly_chart(fig_age, use_container_width=True)

st.subheader("National Volatility Trend Over Time")

trend = monthly.groupby("date")["volatility_score"].mean().reset_index()

fig_trend = px.line(
    trend,
    x="date",
    y="volatility_score"
)

st.plotly_chart(fig_trend, use_container_width=True)

st.caption(
    "This platform uses only aggregated, anonymized Aadhaar data "
    "to support proactive governance and operational planning."
)

