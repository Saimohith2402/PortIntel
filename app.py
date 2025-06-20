import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.calculator import process_transactions, generate_excel_report
from utils.storage import save_portfolio, load_portfolio_names, load_portfolio_data
from utils.suggestions import analyze_portfolio

st.set_page_config(page_title="PortIntel - ML Portfolio Tracker", layout="wide")
st.title("📈 PortIntel: ML-Powered Portfolio Evaluator")

menu = st.sidebar.selectbox("Menu", ["New Portfolio", "Load Portfolio"])

if menu == "New Portfolio":
    st.subheader("➕ Add Transactions")

    if "transactions" not in st.session_state:
        st.session_state.transactions = []

    with st.form("add_transaction"):
        col1, col2, col3 = st.columns(3)
        txn_type = col1.selectbox("Type", ["BUY", "SELL"])
        stock = col2.text_input("Stock Symbol (e.g., TCS.NS)")
        price = col3.number_input("Price", min_value=0.0, step=0.5)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        add_txn = st.form_submit_button("Add Transaction")

    if add_txn:
        st.session_state.transactions.append({
            "stock": stock.upper(),
            "type": txn_type,
            "price": price,
            "quantity": quantity
        })

    if st.session_state.transactions:
        st.subheader("🧾 Transaction List")
        txn_df = pd.DataFrame(st.session_state.transactions)
        st.dataframe(txn_df)

        portfolio_name = st.text_input("Portfolio Name")
        if st.button("✅ Analyze Portfolio"):
            result = process_transactions(st.session_state.transactions)
            if "error" in result:
                st.error(result["error"])
            else:
                df, metrics = result["df"], result["metrics"]

                st.success(f"XIRR: {metrics['xirr']}% | Score: {metrics['score']}/100")

                st.subheader("📊 Holdings Pie Chart")
                fig, ax = plt.subplots()
                ax.pie(df["Weight (%)"], labels=df["Stock"], autopct="%1.1f%%", startangle=140)
                ax.set_title("Portfolio Distribution")
                st.pyplot(fig)

                st.subheader("📋 Portfolio Summary")
                st.dataframe(df)

                st.subheader("🧠 Portfolio Suggestions")
                for tip in analyze_portfolio(df):
                    st.markdown(f"- {tip}")

                excel_bytes = generate_excel_report(df, fig)
                st.download_button("📥 Download Excel Report", excel_bytes, file_name="portfolio_report.xlsx")

                if portfolio_name:
                    save_portfolio(portfolio_name, st.session_state.transactions)
                    st.success(f"Saved as '{portfolio_name}'")
                else:
                    st.warning("Enter a portfolio name to save.")

elif menu == "Load Portfolio":
    st.subheader("📂 Load Existing Portfolio")
    portfolios = load_portfolio_names()
    if portfolios:
        selected = st.selectbox("Choose portfolio", portfolios)
        if st.button("Load"):
            data = load_portfolio_data(selected)
            result = process_transactions(data)
            if "error" in result:
                st.error(result["error"])
            else:
                df, metrics = result["df"], result["metrics"]

                st.success(f"XIRR: {metrics['xirr']}% | Score: {metrics['score']}/100")

                fig, ax = plt.subplots()
                ax.pie(df["Weight (%)"], labels=df["Stock"], autopct="%1.1f%%", startangle=140)
                ax.set_title("Portfolio Distribution")
                st.pyplot(fig)

                st.subheader("📋 Portfolio Summary")
                st.dataframe(df)

                st.subheader("🧠 Portfolio Suggestions")
                for tip in analyze_portfolio(df):
                    st.markdown(f"- {tip}")
    else:
        st.info("No saved portfolios found.")
