import os
import pandas as pd

DATA_FOLDER = "saved_portfolios"
os.makedirs(DATA_FOLDER, exist_ok=True)

def save_portfolio(name, data):
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_FOLDER, f"{name}.csv")
    df.to_csv(file_path, index=False)

def load_portfolio_names():
    return [f.replace(".csv", "") for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

def load_portfolio_data(name):
    file_path = os.path.join(DATA_FOLDER, f"{name}.csv")
    if not os.path.exists(file_path):
        return []
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")