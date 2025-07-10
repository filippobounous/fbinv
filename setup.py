"""Setup script for the fball package."""

from setuptools import setup, find_packages

setup(
    name="fball",
    version="0.1.0",
    packages=find_packages(exclude=("notebooks", "tests*")),
    install_requires=[
        "pandas>=2.2.0",
        "numpy>=1.23.0",
        "pydantic>=2.0",
        "yfinance>=0.2.18",
        "twelvedata>=1.2.25",
        "requests>=2.31.0",
        "openpyxl>=3.1.2",
        "tqdm>=4.66.0",
        "python-dotenv>=1.0.0",
        "fastapi>=0.110",
        "uvicorn>=0.27",
    ],
    python_requires=">=3.11",
)
