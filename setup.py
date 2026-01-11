"""Setup script for KeyPy."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="keypy",
    version="0.1.0",
    author="Saurabh Sharma",
    description="A Python port of KeePassXC password manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samarthya/KeyPy",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pykeepass>=4.0.0",
        "cryptography>=41.0.0",
        "argon2-cffi>=23.0.0",
        "click>=8.1.0",
        "pyperclip>=1.8.0",
        "colorama>=0.4.6",
        "PyQt6>=6.6.0",
        "pyotp>=2.9.0",
        "python-dateutil>=2.8.0",
        "validators>=0.22.0",
        "qrcode>=7.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "keypy=keypy.cli.main:cli",
            "keypy-gui=keypy.gui.main:main",
        ],
    },
)
