import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Product Sales Dashboard")

# Load data
df = pd.read_excel("Product-Sales-Region.xlsx", parse_dates=["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Sidebar filters
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=list(df["Region"].unique()))
products = st.sidebar.multiselect("Product", df["Product"].unique(), default=list(df["Product"].unique()))

filtered = df[
    df["Year"].isin(years) &
    df["Region"].isin(regions) &
    df["Product"].isin(products)
]

# KPI cards
st.subheader("Key Metrics")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"₹{filtered['TotalPrice'].sum():,.0f}")
k2.metric("Total Orders", f"{len(filtered):,}")
k3.metric("Units Sold", f"{filtered['Quantity'].sum():,}")
k4.metric("Return Rate", f"{filtered['Returned'].mean()*100:.1f}%")

st.markdown("---")

# Revenue trend
col1, col2 = st.columns(2)
with col1:
    trend = filtered.groupby("Month")["TotalPrice"].sum().reset_index()
    fig = px.line(trend, x="Month", y="TotalPrice", title="Revenue over time", markers=True)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    by_product = filtered.groupby("Product")["TotalPrice"].sum().reset_index()
    fig2 = px.bar(by_product.sort_values("TotalPrice", ascending=True),
                  x="TotalPrice", y="Product", orientation="h",
                  title="Revenue by product", color="Product")
    st.plotly_chart(fig2, use_container_width=True)

# Region & Salesperson
col3, col4 = st.columns(2)
with col3:
    by_region = filtered.groupby("Region")["TotalPrice"].sum().reset_index()
    fig3 = px.pie(by_region, names="Region", values="TotalPrice", title="Revenue by region")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    by_sales = filtered.groupby("Salesperson")["TotalPrice"].sum().reset_index().sort_values("TotalPrice", ascending=False)
    fig4 = px.bar(by_sales, x="Salesperson", y="TotalPrice", title="Revenue by salesperson", color="Salesperson")
    st.plotly_chart(fig4, use_container_width=True)

# Payment method & Customer type
col5, col6 = st.columns(2)
with col5:
    by_pay = filtered.groupby("PaymentMethod")["TotalPrice"].sum().reset_index()
    fig5 = px.pie(by_pay, names="PaymentMethod", values="TotalPrice", title="Revenue by payment method")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    by_cust = filtered.groupby("CustomerType")["TotalPrice"].sum().reset_index()
    fig6 = px.bar(by_cust, x="CustomerType", y="TotalPrice", title="Revenue by customer type", color="CustomerType")
    st.plotly_chart(fig6, use_container_width=True)

# Data table
st.subheader("Raw Data")
st.dataframe(filtered[["OrderID","Date","Product","Region","Salesperson","Quantity","TotalPrice","Returned","PaymentMethod"]].reset_index(drop=True), use_container_width=True)

# Download
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", csv, "filtered_sales.csv", "text/csv")
