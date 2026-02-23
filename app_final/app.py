import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

st.set_page_config(page_title="MSE Leaderboard", layout="centered")
st.title("🏆 MSE Prediction Leaderboard")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
TARGET_PATH = os.path.join(BASE_DIR, "testing_target.csv")
SCORES_PATH = os.path.join(BASE_DIR, "mse_scores.csv")

# Load or init scores CSV
def load_scores():
    if os.path.exists(SCORES_PATH):
        return pd.read_csv(SCORES_PATH)
    else:
        return pd.DataFrame(columns=["group", "filename", "prediction", "official_MSE"])

def save_scores(df):
    df.to_csv(SCORES_PATH, index=False)

# Load target
@st.cache_data
def load_target():
    return pd.read_csv(TARGET_PATH)

# ── Upload Form ──────────────────────────────────────────────────────────────
st.subheader("📤 Submit Predictions")

with st.form("submission_form"):
    group_name = st.text_input("Group Name")
    prediction_MSE = st.number_input(
        "Your MSE Estimate (0–1)", min_value=0.0, max_value=1.0, step=0.001, format="%.4f"
    )
    uploaded_file = st.file_uploader("Upload CSV (must contain a single numeric column: SalePrice)", type="csv")
    submitted = st.form_submit_button("Submit")

if submitted:
    errors = []

    if not group_name.strip():
        errors.append("Please enter a group name.")
    elif "," in group_name:
        errors.append("Group name cannot contain commas.")

    if uploaded_file is None:
        errors.append("Please upload a CSV file.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            user_df = pd.read_csv(uploaded_file)

            # Validate format
            if list(user_df.columns) != ["SalePrice"]:
                st.error("❌ Invalid file format. The CSV must contain exactly one column named 'SalePrice'.")
            elif not pd.api.types.is_numeric_dtype(user_df["SalePrice"]):
                st.error("❌ The 'SalePrice' column must be numeric.")
            else:
                # Load target and compute MSE
                try:
                    target_df = load_target()
                except FileNotFoundError:
                    st.error(f"❌ Target file not found at: {TARGET_PATH}")
                    st.stop()

                if len(user_df) != len(target_df):
                    st.error(
                        f"❌ Row count mismatch: your file has {len(user_df)} rows, "
                        f"but the target has {len(target_df)} rows."
                    )
                else:
                    official_MSE = float(np.mean((user_df["SalePrice"].values - target_df["SalePrice"].values) ** 2))

                    # Update scores
                    scores_df = load_scores()
                    new_row = pd.DataFrame([{
                        "group": group_name.strip(),
                        "filename": uploaded_file.name,
                        "prediction": round(prediction_MSE, 4),
                        "official_MSE": round(official_MSE, 6),
                    }])
                    scores_df = pd.concat([scores_df, new_row], ignore_index=True)
                    save_scores(scores_df)

                    st.success(
                        f"✅ Submission recorded! Official MSE: **{official_MSE:.6f}** "
                        f"(your estimate was {prediction_MSE:.4f})"
                    )
                    st.cache_data.clear()

        except Exception as ex:
            st.error(f"❌ Error processing file: {ex}")

# ── Leaderboard ───────────────────────────────────────────────────────────────
st.subheader("📊 Leaderboard")

scores_df = load_scores()
print(scores_df.head())

if scores_df.empty:
    st.info("No submissions yet. Be the first to submit!")
else:
    ranked = (
        scores_df
        .sort_values("official_MSE", ascending=True)
        .reset_index(drop=True)
    )
    ranked.index += 1  # 1-based rank
    ranked.index.name = "Rank"
    
    st.dataframe(
        ranked,
        use_container_width=True,
    )