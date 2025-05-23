from ..datasource.registry import all_data_source

def update_all_datasource() -> None:
    for ds in all_data_source:
        ds().update_all_securities(intraday=False)
