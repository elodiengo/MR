import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("Formatted_PO_Data OG.xlsx", sheet_name="MasterData", dtype=str)
    df["GR Qty"] = df["GR Qty"].astype(float)
    df["IR Qty"] = df["IR Qty"].astype(float)
    df["Payment Status"] = df.apply(
        lambda row: "✅ Paid" if row["GR Qty"] == row["IR Qty"] and row["GR Qty"] > 0
        else ("❌ Not Started" if row["GR Qty"] == 0 and row["IR Qty"] == 0
        else "⏳ Pending"), axis=1)
    return df

df = load_data()

# --- Filters ---
st.title("📦 PO Payment Dashboard")

cols = st.columns(5)
with cols[0]: mr_filter = st.text_input("🔍 MR")
with cols[1]: net_num_filter = st.text_input("📡 Network Number")
with cols[2]: net_name_filter = st.text_input("🏷️ Network Name")
with cols[3]: po_doc_filter = st.text_input("📑 Purchasing Document")
with cols[4]: hwm_filter = st.text_input("👤 HWMDS")

# --- Apply Filters ---
filtered_df = df.copy()
if mr_filter: filtered_df = filtered_df[filtered_df["MR"].str.contains(mr_filter, case=False, na=False)]
if net_num_filter: filtered_df = filtered_df[filtered_df["Network Number"].str.contains(net_num_filter, case=False, na=False)]
if net_name_filter: filtered_df = filtered_df[filtered_df["Network Name"].str.contains(net_name_filter, case=False, na=False)]
if po_doc_filter: filtered_df = filtered_df[filtered_df["Purchasing Document"].str.contains(po_doc_filter, case=False, na=False)]
if hwm_filter: filtered_df = filtered_df[filtered_df["HWMDS"].str.contains(hwm_filter, case=False, na=False)]

# --- Show Data ---
st.dataframe(filtered_df, use_container_width=True)

# --- Download Button ---
st.download_button("📥 Download Report", filtered_df.to_csv(index=False), file_name="PO_Report.csv")
