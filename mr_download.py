import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("Formatted_PO_Data OG.xlsx", sheet_name="MasterData", dtype=str)
    df["GR Qty"] = df["GR Qty"].astype(float)
    df["IR Qty"] = df["IR Qty"].astype(float)
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

# --- Apply Filters ---
filtered_df = df.copy()
if mr_filter: filtered_df = filtered_df[filtered_df["MR"].str.contains(mr_filter, case=False, na=False)]
if net_num_filter: filtered_df = filtered_df[filtered_df["Network Number"].str.contains(net_num_filter, case=False, na=False)]
if net_name_filter: filtered_df = filtered_df[filtered_df["Network Name"].str.contains(net_name_filter, case=False, na=False)]
if po_doc_filter: filtered_df = filtered_df[filtered_df["Purchasing Document"].str.contains(po_doc_filter, case=False, na=False)]
if hwm_filter: filtered_df = filtered_df[filtered_df["HWMDS"].str.contains(hwm_filter, case=False, na=False)]

cols = list(filtered_df.columns)
cols.remove("Payment Status")
insert_pos = cols.index("Purchasing Document") + 1
cols.insert(insert_pos, "Payment Status")
filtered_df = filtered_df[cols]

# Build interactive grid options
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)

gb.configure_column(
    "Net Price",
    type=["numericColumn"],
    valueFormatter="Number(parseFloat(params.value).toFixed(2))"
)

gb.configure_column(
    "Total Line Item Price",
    type=["numericColumn"],
    valueFormatter="Number(parseFloat(params.value).toFixed(2))"
)

gb.configure_column("Shopping Cart", hide=True)
gb.configure_column("REMOTE/INDOOR", hide=True)
gb.configure_column("Vendor No", hide=True)
gb.configure_column("GR/IR Mismatch", hide=True)
gb.configure_column("IR Document No.", hide=True)
gb.configure_column("Invoice Date.", hide=True)
gb.configure_column("Invoice Due Date.", hide=True)
grid_options = gb.build()

# Render the AgGrid table
AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    height=800,
    fit_columns_on_grid_load=False,  # Disable this so autoSize works better
    autoSizeAllColumns=True
)
