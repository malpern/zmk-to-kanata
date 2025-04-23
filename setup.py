from setuptools import setup, find_packages

setup(
    name="zmk-kanata-converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "pytest",
        "black",
        "ruff",
    ],
    entry_points={
        "console_scripts": [
            "zmk-kanata=converter.main:main",
        ],
    },
    python_requires=">=3.8",
    description="Convert ZMK keymaps to Kanata configuration",
    author="Nick Tokatana",
    author_email="nick@tokatana.com",
    url="https://github.com/nicktokatana/zmk-kanata",
)
