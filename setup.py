from setuptools import setup

setup(
    name="sending",
    version="0.0.2",
    url="https://github.com/ehatton/sending",
    author="Emma Hatton-Ellis",
    author_email="ehattonellis@gmail.com",
    license="MIT",
    py_modules=["sending"],
    install_requires=["click", "pysftp", "requests"],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["sending=sending.cli:cli",],},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)

