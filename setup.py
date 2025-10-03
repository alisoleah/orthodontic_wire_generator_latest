
# ================================================================
# setup.py (for proper package installation)
"""
Setup configuration for the Modular Orthodontic Wire Generator package.

This would be a separate file in the project root: setup.py
"""

SETUP_PY_CONTENT = '''
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orthodontic-wire-generator",
    version="3.0.0",
    author="Wire Generator Project",
    description="Modular system for generating custom orthodontic wires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "open3d>=0.15.0",
        "scipy>=1.7.0",
        "tkinter",  # Usually included with Python
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "wire-generator=main:main",
            "wire-gui=main:main_gui",
        ],
    },
)
'''
