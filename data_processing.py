import pandas as pd
import utils


def process_uidai_data(df):
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

    monthly["volatility_flag"] = monthly["volatility_score"].apply(
        utils.classify_volatility
    )

    latest = monthly.sort_values("date").groupby(
        ["state", "district", "age_group"]
    ).tail(1)

    state_risk = latest.groupby("state")["volatility_score"].mean().reset_index()
    state_risk["volatility_flag"] = state_risk["volatility_score"].apply(
        utils.classify_volatility
    )

    age_summary = latest.groupby(
        ["state", "age_group"]
    )["volatility_score"].mean().reset_index()

    trend = monthly.groupby("date")["volatility_score"].mean().reset_index()

    return {
        "monthly": monthly,
        "latest": latest,
        "state_risk": state_risk,
        "age_summary": age_summary,
        "trend": trend
    }
