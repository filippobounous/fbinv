from setuptools import setup, find_packages

setup(
    name="investment",
    version="0.1.0",
    packages=find_packages(exclude=("notebooks")),
    install_requires=[
        "pandas",
        "numpy",
        "pydantic",
        "yfinance",
        "twelvedata",
        "requests",
        "openpyxl",
        "python-dotenv",
    ],
    python_requires=">=3.9",
)
