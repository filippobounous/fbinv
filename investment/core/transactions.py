"""Logic for extracting and storing portfolio transactions."""

import pandas as pd
from pydantic import BaseModel

from ..config import TRANSACTION_PATH, TRANSACTION_SHEET_NAME, PORTFOLIO_PATH, DEFAULT_NAME

class Transactions(BaseModel):
    """Utility class for working with transaction spreadsheets."""
    code: str = DEFAULT_NAME
    file_path: str = TRANSACTION_PATH
    sheet_name: str = TRANSACTION_SHEET_NAME
    portfolio_path: str = PORTFOLIO_PATH

    def extract_and_save_investment_transactions(self) -> None:
        """
        Custom method to extract transactions from a given .xlsx sheet into a Portfolio csv.
        """
        import_df = self._load_transactions()

        transactions = import_df.loc[
            import_df.Category == "Investments"
        ][["Description", "Origin", "Date"]]

        pattern = (
            r'^\s*'              # optional leading whitespace
            r'(?P<figi_code>\S+)\s+'     # security code (non-whitespace)
            r'(?P<direction>\S)\s+'      # direction (single character, e.g. 'B')
            r'(?P<quantity>[\d\.]+)\s+'  # quantity (digits and decimals)
            r'(?P<price>[\d\.]+)\s+'     # price (digits and decimals)
            r'(?P<currency>\S+)\s*$'     # currency (non-whitespace) + optional trailing whitespace
        )

        df = transactions["Description"].str.extract(pattern)
        df["quantity"] = df["quantity"].astype(float)
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"] * df["direction"].map({"B": 1, "S": -1}).fillna(0)
        df["account"] = transactions["Origin"].str[:-3]
        df["value"] = df["quantity"] * df["price"]
        df["as_of_date"] = pd.to_datetime(transactions["Date"])
        
        df = df.drop(columns=["direction"])
        df = df.sort_values(['figi_code', 'as_of_date']).reset_index(drop=True)
        
        df.to_csv(f"{self.portfolio_path}/{self.code}-transactions.csv", index=False)

    def load_and_save_cash_positions(self) -> None:
        """
        Custom method to extract cash positions from a given .xlsx sheet into a Portfolio csv.
        """
        import_df = self._load_transactions()
        import_df = import_df.set_index("Date")
        
        df = (
            import_df[["Currency", "Net Value"]]
            .sort_index()
            .groupby(["Currency"])
            .expanding()
            .sum()
        ).reset_index().rename(columns={
            "Date": "as_of_date",
            "Currency": "currency",
            "Net Value": "value",
        })
        
        df["value"] = df["value"].round(2)
        df["change"] = df.groupby("currency")["value"].diff().fillna(df["value"])
        df["change"] = df["change"].round(2)

        df.to_csv(f"{self.portfolio_path}/{self.code}-cash.csv", index=False)

    def _load_transactions(self) -> pd.DataFrame:
        """Load the raw transaction data from disk."""

        return pd.read_excel(self.file_path, sheet_name=self.sheet_name)
    
    def update(self) -> None:
        """Refresh both transaction and cash CSV files."""

        self.extract_and_save_investment_transactions()
        self.load_and_save_cash_positions()
