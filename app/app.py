import streamlit as st
import pandas as pd

st.title("CSV Validator")
st.write("Upload a CSV file with a single column named `SalePrice` containing numbers.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if df.shape[1] != 1:
            st.error(f"❌ Failure: The file must have exactly 1 column, but found {df.shape[1]}.")
        elif df.columns[0] != "SalePrice":
            st.error(f"❌ Failure: The column must be named 'SalePrice', but found '{df.columns[0]}'.")
        elif not pd.to_numeric(df["SalePrice"], errors="coerce").notna().all():
            st.error("❌ Failure: The 'SalePrice' column must contain only numbers.")
        else:
            st.success("✅ Success! The file has a single numeric 'SalePrice' column.")
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Failure: Could not read the file. Error: {e}")