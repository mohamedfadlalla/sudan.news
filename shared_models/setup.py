from setuptools import setup, find_packages

setup(
    name="shared_models",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=1.4.0",
        "alembic>=1.7.0",
        "python-dotenv>=0.19.0",
        "pytest>=7.0.0",
    ],
)
