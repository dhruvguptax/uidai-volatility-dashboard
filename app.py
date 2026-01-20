import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="UIDAI Demographic Volatility Platform",
    layout="wide"
)

st.title("UIDAI Demographic Volatility Monitoring Platform")
st.caption("Early-warning signals for demographic stress using aggregated Aadhaar update data")

# =========================
# INTRO / STORY
# =========================
st.markdown("""
## 🧩 What Problem Are We Solving?

UIDAI manages Aadhaar enrolment and demographic update infrastructure across India.  
However, demand for updates is **uneven and unpredictable**, driven by:

- Migration
- Seasonal population movement
- Lifecycle transitions (children, youth, adults)

Today, infrastructure stress is often handled **after congestion occurs**.

---

## 💡 What This Platform Does

This platform acts as an **early-warning system** by analysing **aggregated Aadhaar demographic update data** to:

- Detect abnormal volatility patterns
- Identify states under demographic churn
- Support **proactive operational planning**

⚠️ No individual-level or sensitive data is used.
""")


st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload Aggregated UIDAI CSV",
    type=["csv"],
    help="Upload monthly aggregated Aadhaar demographic update data (CSV format)"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom dataset loaded")
else:
    df = pd.read_csv("data/uidai_data.csv")
    st.sidebar.info("Using default sample dataset")


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


def classify(score):
    if score < 0.2:
        return "Low Volatility"
    elif score < 0.5:
        return "Moderate Volatility"
    else:
        return "High Volatility"

monthly["volatility_flag"] = monthly["volatility_score"].apply(classify)


latest = monthly.sort_values("date").groupby(
    ["state", "district", "age_group"]
).tail(1)


state_risk = latest.groupby("state")["volatility_score"].mean().reset_index()
state_risk["volatility_flag"] = state_risk["volatility_score"].apply(classify)


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

state_risk["lat"] = state_risk["state"].apply(lambda x: state_coords.get(x, (None, None))[0])
state_risk["lon"] = state_risk["state"].apply(lambda x: state_coords.get(x, (None, None))[1])
state_risk = state_risk.dropna(subset=["lat", "lon"])


st.subheader("National Risk Snapshot")

c1, c2, c3 = st.columns(3)

c1.metric("Total States", state_risk.shape[0])
c2.metric(
    "High Volatility States",
    (state_risk["volatility_flag"] == "High Volatility").sum()
)
c3.metric(
    "Moderate Volatility States",
    (state_risk["volatility_flag"] == "Moderate Volatility").sum()
)


st.subheader("India Demographic Volatility Map")

fig_map = px.scatter_geo(
    state_risk,
    lat="lat",
    lon="lon",
    color="volatility_flag",
    size="volatility_score",
    hover_name="state",
    projection="natural earth"
)

fig_map.update_geos(
    scope="asia",
    center=dict(lat=22.5, lon=78.9),
    projection_scale=4
)

st.plotly_chart(fig_map, use_container_width=True)


st.subheader("State-Level Volatility Ranking")

fig_state = px.bar(
    state_risk.sort_values("volatility_score", ascending=False),
    x="state",
    y="volatility_score",
    color="volatility_flag"
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


st.markdown("""
## 🛠 How Should This Be Used?

- **High Volatility** → temporary enrolment kits, staffing surge  
- **Moderate Volatility** → monitoring & preparedness  
- **Rising national trend** → pre-emptive allocation before congestion  

This enables UIDAI to move from **reactive service delivery** to **proactive governance**.
""")

st.caption(
    "This dashboard uses only aggregated, anonymized Aadhaar data and is intended "
    "for policy analysis and operational planning."
)
