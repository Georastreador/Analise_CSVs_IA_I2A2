from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="csv-analysis-ai",
    version="2.0.0",
    author="CSV Analysis AI Team",
    author_email="contato@csvanalysisai.com",
    description="Sistema de análise inteligente de dados CSV com agentes de IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/csv-analysis-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "csv-analysis-ai=csv_analysis_app_v2:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.toml"],
    },
    keywords="csv analysis ai machine-learning data-science streamlit crewai",
    project_urls={
        "Bug Reports": "https://github.com/seu-usuario/csv-analysis-ai/issues",
        "Source": "https://github.com/seu-usuario/csv-analysis-ai",
        "Documentation": "https://github.com/seu-usuario/csv-analysis-ai/wiki",
    },
)
