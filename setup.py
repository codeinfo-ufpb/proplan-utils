from setuptools import setup, find_packages

setup(
    name="proplan-tools",
    version="1.0",
    author="PROPLAN CODEINFO",
    description="Biblioteca Modular para integração, formatação, extração e normalização de dados na área de informação, ciência de dados e inteligência da PROPLAN/UFPB",
    packages=find_packages(),
    install_requires=[
        "pandas", "sqlalchemy", "python-dotenv", "setuptools", "psycopg2"
    ],
)