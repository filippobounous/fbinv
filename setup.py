from setuptools import setup, find_packages

setup(
    name="investment",
    version="0.1.0",
    packages=find_packages(exclude=("notebooks")),
    install_requires=[
        "pandas",
        "numpy",
        "pydantic",
        "fastapi",
        "uvicorn",
        "yfinance",
        "twelvedata",
        "requests",
        "openpyxl",
        "tqdm",
        "python-dotenv",
    ],
    python_requires=">=3.9",
)
