import streamlit as st
import pandas as pd
import plotly.express as px

from data_processing import process_uidai_data
from utils import get_state_coords


st.set_page_config(
    page_title="UIDAI Demographic Volatility Platform",
    layout="wide"
)

st.title("UIDAI Demographic Volatility Monitoring Platform")
st.caption(
    "Early-warning signals for demographic stress using aggregated Aadhaar update data"
)


st.markdown("""
## 🧩 What Problem Are We Solving?

UIDAI manages Aadhaar enrolment and demographic update infrastructure across India.  
However, demand for demographic updates is **uneven and unpredictable**, driven by:

- Migration
- Seasonal population movement
- Lifecycle transitions

Currently, operational stress is often addressed **after congestion occurs**.

---

## 💡 What This Platform Does

This platform provides an **early-warning system** by analysing **aggregated Aadhaar demographic update data** to:

- Detect abnormal volatility patterns
- Identify states under demographic churn
- Support **proactive resource planning**

🔐 No individual-level or sensitive data is used.
""")


st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload Aggregated UIDAI CSV",
    type=["csv"],
    help="Upload monthly aggregated Aadhaar demographic update data (CSV)"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom dataset loaded")
else:
    df = pd.read_csv("data/uidai_data.csv")
    st.sidebar.info("Using default sample dataset")


outputs = process_uidai_data(df)

monthly = outputs["monthly"]
latest = outputs["latest"]
state_risk = outputs["state_risk"]
age_summary = outputs["age_summary"]
trend = outputs["trend"]

state_risk["lat"] = state_risk["state"].apply(lambda x: get_state_coords(x)[0])
state_risk["lon"] = state_risk["state"].apply(lambda x: get_state_coords(x)[1])
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
    color="volatility_flag",
    labels={
        "volatility_score": "Average Volatility Score",
        "state": "State"
    }
)

st.plotly_chart(fig_state, use_container_width=True)


st.subheader("Age Group Comparison")

fig_age = px.bar(
    age_summary,
    x="state",
    y="volatility_score",
    color="age_group",
    labels={
        "volatility_score": "Average Volatility Score",
        "state": "State",
        "age_group": "Age Group"
    }
)

st.plotly_chart(fig_age, use_container_width=True)


st.subheader("National Volatility Trend Over Time")

fig_trend = px.line(
    trend,
    x="date",
    y="volatility_score",
    labels={
        "date": "Date",
        "volatility_score": "Average Volatility Score"
    }
)

st.plotly_chart(fig_trend, use_container_width=True)


st.markdown("""
## 🛠 How Should This Be Used?

- **High Volatility** → temporary enrolment kits, staffing surge  
- **Moderate Volatility** → monitoring & preparedness  
- **Rising national trend** → pre-emptive allocation before congestion  

This enables UIDAI to shift from **reactive service delivery** to **proactive governance**.
""")

st.caption(
    "This dashboard uses only aggregated, anonymized Aadhaar data and is intended "
    "for policy analysis and operational decision support."
)
