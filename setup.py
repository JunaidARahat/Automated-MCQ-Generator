# installing local packages in the virtual enviorment is done by setup.-py

from setuptools import find_packages, setup

setup(
    name='mcq_generator',
    version="0.0.1",
    author="JunaidARahat",
    author_email="mjunaidrahat1990@gmail.com",
    install_requires=["openai", "langchain", "streamlit", "python-dotenv", "PyPDF2"],
    packages=find_packages()
    # find_packages() -> responsible for finding the local packages in  my folders
)