import pandas as pd

class FakeLocalDataSource:
    name = "local"

    security_mapping_df = pd.DataFrame([
        {
            "code": "AAA",
            "figi_code": "AAA111",
            "name": "Company AAA",
            "reporting_currency": "USD",
            "currency": "USD",
            "multiplier": 1.0,
            "type": "equity",
        },
        {
            "code": "BBB",
            "figi_code": "BBB222",
            "name": "Company BBB",
            "reporting_currency": "USD",
            "currency": "USD",
            "multiplier": 1.0,
            "type": "equity",
        },
        {
            "code": "USDGBP",
            "figi_code": "CCY1",
            "name": "USDGBP",
            "reporting_currency": "USD",
            "currency": "USD",
            "multiplier": 1.0,
            "type": "currency_cross",
        },
    ])

    portfolio_mapping_df = pd.DataFrame([
        {"code": "PORT", "owner": "Tester", "has_cash": False}
    ])

    reporting_currency_df = pd.DataFrame([
        {"reporting_currency": "USD", "currency": "USD", "multiplier": 1.0}
    ])

    def __init__(self, *args, **kwargs):
        pass

    @property
    def portfolio_mapping(self):
        return self.__class__.portfolio_mapping_df

    @property
    def reporting_currency(self):
        return self.__class__.reporting_currency_df

    def load_portfolio(self, portfolio):
        row = self.portfolio_mapping[self.portfolio_mapping.code == portfolio.code]
        return row.iloc[0].to_dict()

    def load_security(self, security):
        row = self.security_mapping_df[self.security_mapping_df.code == security.code]
        return row.iloc[0].to_dict()

    def load_composite_security(self, composite):
        di = composite.security.model_dump()
        di.pop("code", None)
        di["currency"] = composite.currency_cross.currency
        return di

    def load_generic_security(self, **kwargs):
        from investment.core.security.registry import security_registry
        row = self.security_mapping_df[self.security_mapping_df.code == kwargs["code"]]
        entity_type = row.iloc[0].type
        entity = security_registry[entity_type]
        return entity(**kwargs)

    def get_security_mapping(self):
        return self.__class__.security_mapping_df
