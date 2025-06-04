from setuptools import setup, find_packages

setup(
    name="news_crawler_ver_4",
    version="4.2.7",
    description="News crawler system with anti-403 features and multiple extraction methods",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "tqdm>=4.66.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
        ]
    }
)
