from setuptools import setup

setup(
    name="sending",
    version="0.0.1",
    url="https://github.com/ehatton/sending",
    author="Emma Hatton-Ellis",
    author_email="ehattonellis@gmail.com",
    license="MIT",
    py_modules=["sending"],
    install_requires=["click"],
    python_requires=">=3.8",
    entry_points="""
        [console_scripts]
        sending=sending.cli:cli
    """,
)
