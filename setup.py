from setuptools import setup

with open("sending/version.py", "r") as infile:
    exec(infile.read())

setup(
    name="sending",
    version=__version__,  # type: ignore
    url="https://github.com/ehatton/sending",
    author="Emma Hatton-Ellis",
    author_email="ehattonellis@gmail.com",
    license="MIT",
    packages=["sending"],
    install_requires=[
        "click",
        "colorama; platform_system=='Windows'",
        "pysftp",
        "requests",
    ],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["sending=sending.cli:cli",],},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)
