import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import date

st.set_page_config(layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("Formatted_PO_Data OG.xlsx", sheet_name="MasterData", dtype=str)
    df["GR Qty"] = df["GR Qty"].astype(float)
    df["IR Qty"] = df["IR Qty"].astype(float)

    df["PO Released Date"] = pd.to_datetime(df["PO Released Date"], errors="coerce")

    df["Payment Status"] = df.apply(
        lambda row: (
            "✅ Paid" if row["GR Qty"] == row["IR Qty"] and row["GR Qty"] > 0 else
            "❌ Not Started" if row["GR Qty"] == 0 and row["IR Qty"] == 0 else
            "⏳ Payment Pending - Good Receipts" if row["GR Qty"] < row["IR Qty"] else
            "⏳ Payment Pending - Missing Supplier Invoice"
        ),
        axis=1
    )
    return df

df = load_data()

# --- Filters ---
st.title("📦 PO Payment Dashboard")

cols = st.columns(5)
with cols[0]: mr_filter = st.text_input("MR")
with cols[1]: net_num_filter = st.text_input("Network Number")
with cols[2]: net_name_filter = st.text_input("Network Name")
with cols[3]: po_doc_filter = st.text_input("PO Number")
with cols[4]: hwm_filter = st.text_input("HWMDS")

# --- PO Released Date Filter ---
st.markdown("### 📅 Filter by PO Released Date")
min_date = df["PO Released Date"].min().date() if df["PO Released Date"].notnull().any() else date(2000, 1, 1)
max_date = df["PO Released Date"].max().date() if df["PO Released Date"].notnull().any() else date.today()

from_date = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

# --- Apply Filters ---
filtered_df = df.copy()
if mr_filter: filtered_df = filtered_df[filtered_df["MR"].str.contains(mr_filter, case=False, na=False)]
if net_num_filter: filtered_df = filtered_df[filtered_df["Network Number"].str.contains(net_num_filter, case=False, na=False)]
if net_name_filter: filtered_df = filtered_df[filtered_df["Network Name"].str.contains(net_name_filter, case=False, na=False)]
if po_doc_filter: filtered_df = filtered_df[filtered_df["Purchasing Document"].str.contains(po_doc_filter, case=False, na=False)]
if hwm_filter: filtered_df = filtered_df[filtered_df["HWMDS"].str.contains(hwm_filter, case=False, na=False)]

# ✅ Filter by PO Released Date Range
filtered_df = filtered_df[
    (filtered_df["PO Released Date"] >= pd.to_datetime(from_date)) &
    (filtered_df["PO Released Date"] <= pd.to_datetime(to_date))
]

# --- Reorder columns: move Payment Status beside Purchasing Document
cols = list(filtered_df.columns)
if "Payment Status" in cols and "Purchasing Document" in cols:
    cols.remove("Payment Status")
    insert_pos = cols.index("Purchasing Document") + 1
    cols.insert(insert_pos, "Payment Status")
    filtered_df = filtered_df[cols]

# --- Clean numeric columns
filtered_df["Net Price"] = pd.to_numeric(filtered_df["Net Price"], errors="coerce").round(2)
filtered_df["Total Line Item Price"] = pd.to_numeric(filtered_df["Total Line Item Price"], errors="coerce").round(2)

# Optional formatting as strings with 2 decimals (for display only)
filtered_df["Net Price"] = filtered_df["Net Price"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
filtered_df["Total Line Item Price"] = filtered_df["Total Line Item Price"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

# --- Build AgGrid table
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)

# Hide unnecessary columns
gb.configure_column("Shopping Cart", hide=True)
gb.configure_column("REMOTE/INDOOR", hide=True)
gb.configure_column("Vendor No", hide=True)
gb.configure_column("GR/IR Mismatch", hide=True)
gb.configure_column("IR Document No.", hide=True)
gb.configure_column("Invoice Date.", hide=True)
gb.configure_column("Invoice Due Date.", hide=True)

grid_options = gb.build()

# --- Show table
AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    height=800,
    fit_columns_on_grid_load=False,
    autoSizeAllColumns=True
)
