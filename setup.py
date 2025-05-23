from setuptools import setup, find_packages

setup(
    name="investment",
    version="0.1.0",
    packages=find_packages(exclude=("notebooks")),
    install_requires=[
        "pandas",
        "pydantic",
        "yfinance",
        "twelvedata",
        "requests",
        "openpyxl",
        "python-dotenv",
        "alpha_vantage",
    ],
    python_requires=">=3.9",
)
