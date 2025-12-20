import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

# --------------------------
# App Config
# --------------------------
st.set_page_config(page_title="AI Expense Analyzer", page_icon="💰", layout="wide")
st.title("💰 AI Expense Analyzer")
st.markdown("Track your expenses, visualize spending patterns, and get smart AI suggestions!")

# --------------------------
# Get API key from Secrets / Environment
# --------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------
# Session State
# --------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Description"]
    )

# --------------------------
# Expense Input
# --------------------------
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form"):
        date = st.date_input("Date")
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Entertainment", "Bills", "Other"]
        )
        amount = st.number_input("Amount (in PKR)", min_value=0.0, step=100.0)
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            new_row = pd.DataFrame(
                [[date, category, amount, description]],
                columns=["Date", "Category", "Amount", "Description"]
            )
            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_row],
                ignore_index=True
            )
            st.success("✅ Expense added successfully!")

# --------------------------
# Display & Charts
# --------------------------
if not st.session_state.expenses.empty:
    st.subheader("📊 Expense Records")
    st.dataframe(st.session_state.expenses, use_container_width=True)

    st.subheader("🧩 Expense Distribution by Category")
    cat_sum = st.session_state.expenses.groupby("Category")["Amount"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(cat_sum, labels=cat_sum.index, autopct="%1.1f%%")
    st.pyplot(fig1)

    st.subheader("📈 Spending Trend Over Time")
    trend = (
        st.session_state.expenses
        .groupby("Date")["Amount"]
        .sum()
        .reset_index()
    )
    fig2, ax2 = plt.subplots()
    ax2.plot(trend["Date"], trend["Amount"], marker="o")
    st.pyplot(fig2)

    # --------------------------
    # AI Analysis
    # --------------------------
    st.subheader("🤖 AI Expense Insights")

    if not GROQ_API_KEY:
        st.warning("⚠️ GROQ_API_KEY not set. Add it in Secrets.")
    else:
        client = Groq(api_key=GROQ_API_KEY)
        data_text = st.session_state.expenses.to_string(index=False)

        if st.button("Analyze My Expenses 💬"):
            with st.spinner("Analyzing..."):
                try:
                    prompt = f"""
                    Analyze this expense data and provide:
                    1. Spending patterns
                    2. Overspending categories
                    3. Saving tips
                    4. Financial health summary

                    Data:
                    {data_text}
                    """

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                    )

                    st.success("✅ Analysis Complete!")
                    st.markdown(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
else:
    st.info("💡 Add some expenses above to get started!")
