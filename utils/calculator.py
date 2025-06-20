import pandas as pd
import yfinance as yf
import datetime
import io
from scipy.optimize import newton
import xlsxwriter

def xirr(cashflows, dates):
    def xnpv(rate):
        return sum([
            cf / (1 + rate) ** ((d - dates[0]).days / 365)
            for cf, d in zip(cashflows, dates)
        ])
    return newton(xnpv, 0.1)

def calculate_score(xirr_value, benchmark=12):
    return max(0, min(100, 50 + (xirr_value - benchmark) * 2))

def process_transactions(transactions):
    try:
        df_txn = pd.DataFrame(transactions)
        df_txn["stock"] = df_txn["stock"].str.upper()
        today = datetime.datetime.now().date()

        summary = {}
        for _, row in df_txn.iterrows():
            stock = row["stock"]
            qty = row["quantity"] if row["type"] == "BUY" else -row["quantity"]
            value = row["quantity"] * row["price"] * (1 if row["type"] == "BUY" else -1)

            if stock not in summary:
                summary[stock] = {"net_qty": 0, "invested": 0, "buys": [], "sells": []}
            summary[stock]["net_qty"] += qty
            summary[stock]["invested"] += value

            if row["type"] == "BUY":
                summary[stock]["buys"].append((row["price"], row["quantity"]))
            else:
                summary[stock]["sells"].append((row["price"], row["quantity"]))

            total_bought = sum(q for _, q in summary[stock]["buys"])
            total_sold = sum(q for _, q in summary[stock]["sells"])
            if total_sold > total_bought:
                return {"error": f"❌ Sold more shares than bought for {stock}"}

        records = []
        cashflows = []
        dates = []
        missing_stocks = []

        for stock, data in summary.items():
            if data["net_qty"] <= 0:
                continue

            try:
                live_price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
            except:
                live_price = data["buys"][-1][0]
                missing_stocks.append(stock)

            current_value = data["net_qty"] * live_price

            total_invested = sum(p * q for p, q in data["buys"])
            total_sell_proceeds = sum(p * q for p, q in data["sells"])
            adjusted_invested = max(0, total_invested - total_sell_proceeds)

            avg_price = total_invested / sum(q for _, q in data["buys"])
            if adjusted_invested == 0:
                return_pct = float('inf')
            else:
                return_pct = ((current_value - adjusted_invested) / adjusted_invested) * 100

            records.append({
                "Stock": stock,
                "Net Quantity": data["net_qty"],
                "Avg Buy Price": round(avg_price, 2),
                "Live Price": round(live_price, 2),
                "Invested Amount": round(adjusted_invested, 2),
                "Current Value": round(current_value, 2),
                "Return (%)": "∞" if return_pct == float('inf') else round(return_pct, 2)
            })

            for price, qty in data["buys"]:
                cashflows.append(-price * qty)
                dates.append(today - datetime.timedelta(days=365))
            for price, qty in data["sells"]:
                cashflows.append(price * qty)
                dates.append(today - datetime.timedelta(days=180))
            cashflows.append(current_value)
            dates.append(today)

        df = pd.DataFrame(records)
        total_value = df["Current Value"].sum()
        df["Weight (%)"] = round((df["Current Value"] / total_value) * 100, 2)

        xirr_value = round(xirr(cashflows, dates) * 100, 2)
        score = calculate_score(xirr_value)

        return {
            "df": df,
            "metrics": {"xirr": xirr_value, "score": score},
            "missing": missing_stocks
        }
    except Exception as e:
        return {"error": f"⚠️ Calculation error: {str(e)}"}

def generate_excel_report(df, chart_figure):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Portfolio", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Portfolio"]

        chart_path = "temp_chart.png"
        chart_figure.savefig(chart_path)
        worksheet.insert_image("J2", chart_path)

    output.seek(0)
    return output.read()
