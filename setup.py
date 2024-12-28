from setuptools import setup, find_packages

setup(
    name="github-sentinel",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "github-sentinel=src.main:main",
        ],
    },
) 