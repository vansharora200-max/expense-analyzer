import streamlit as st
import plotly.express as px
import pandas as pd
import tempfile, os
from analyzer import load_data, get_category_totals, get_monthly_totals, get_top_transactions, get_budget_analysis

st.set_page_config(page_title="Expense Analyzer", page_icon="💰", layout="wide")

st.title("💰 Expense Analyzer & Budget Advisor")
st.markdown("Upload your expense CSV to get started.")

# Sample download button
with open("data/sample.csv", "rb") as f:
    st.download_button(
        label="Download sample CSV to try",
        data=f,
        file_name="sample_expenses.csv",
        mime="text/csv"
    )

uploaded_file = st.file_uploader("Upload your expense file", type=["csv", "xlsx"])

if uploaded_file is not None:
    suffix = ".csv" if uploaded_file.name.endswith(".csv") else ".xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        df = load_data(tmp_path)
        os.unlink(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        st.error("Could not read this file. Make sure it has columns: date, description, amount, category.")
        st.stop()

    st.success(f"Loaded {len(df)} transactions successfully!")

    # Overview metrics
    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"₹{df['amount'].sum():,.0f}")
    col2.metric("Transactions", len(df))
    col3.metric("Categories", df['category'].nunique())

    st.divider()

    # Charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Spending by category")
        cat_totals = get_category_totals(df).reset_index()
        cat_totals.columns = ['category', 'amount']
        fig_pie = px.pie(cat_totals, values='amount', names='category', hole=0.4)
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("Monthly spending")
        monthly = get_monthly_totals(df).reset_index()
        monthly.columns = ['month', 'amount']
        fig_bar = px.bar(monthly, x='month', y='amount', color='amount',
                         color_continuous_scale='Blues')
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Top transactions
    st.subheader("Top 5 transactions")
    top = get_top_transactions(df)
    top['amount'] = top['amount'].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(top, use_container_width=True, hide_index=True)

    st.divider()

    # Budget advisor
    st.subheader("Budget advisor")
    st.markdown("Set a monthly budget for each category and see how you're doing.")

    categories = df['category'].unique().tolist()
    budget = {}

    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cols[i]:
            budget[cat] = st.number_input(
                f"{cat.capitalize()}",
                min_value=0,
                value=2000,
                step=100
            )

    if st.button("Analyze budget"):
        analysis = get_budget_analysis(df, budget)
        for _, row in analysis.iterrows():
            if row['status'] == "over":
                st.error(
                    f"**{row['category'].capitalize()}** — "
                    f"You spent ₹{row['spent']:,.0f} against a budget of ₹{row['budget']:,.0f}. "
                    f"You are **₹{row['difference']:,.0f} over budget.**"
                )
            else:
                st.success(
                    f"**{row['category'].capitalize()}** — "
                    f"You spent ₹{row['spent']:,.0f} against a budget of ₹{row['budget']:,.0f}. "
                    f"You have **₹{row['difference']:,.0f} remaining.**"
                )

else:
    st.info("No file uploaded yet. Download the sample CSV above to try it out.")

# Footer
st.divider()
st.markdown(
    "<div style='text-align:center; color:gray; font-size:13px;'>Built with Python, pandas, Streamlit & Plotly</div>",
    unsafe_allow_html=True
)