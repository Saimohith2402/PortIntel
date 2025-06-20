def analyze_portfolio(df):
    tips = []
    if df.empty:
        return ["Portfolio is empty. Please add stocks."]

    for _, row in df.iterrows():
        stock = row["Stock"]
        weight = row["Weight (%)"]
        return_str = row["Return (%)"]

        try:
            return_pct = float(return_str)
        except:
            return_pct = None

        if weight > 40:
            tips.append(f"⚠️ High concentration in {stock} ({weight}%). Consider diversification.")
        if return_pct is not None and return_pct < -10:
            tips.append(f"🔻 {stock} is down {return_pct}%. Evaluate fundamentals or rebalance.")
        if weight > 25 and return_pct is not None and return_pct < 5:
            tips.append(f"🧐 {stock} has high weight but low return ({return_pct}%). Reassess your allocation.")

    if len(df) < 3:
        tips.append("📉 Less than 3 holdings. Consider adding more stocks for diversification.")
    tips.append("🧠 Try to diversify across sectors to reduce risk.")

    return tips
