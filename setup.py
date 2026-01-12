"""
Setup script dla Jan Subagent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jan-subagent",
    version="1.0.0",
    author="Jan Subagent Team",
    author_email="your@email.com",
    description="Subagent MCP Jana Kochanowskiego do korekty języka polskiego",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jan-server=jan.jan_subagent:main",
        ],
    },
    keywords="mcp subagent polish language correction kochanowski bielik",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/jan/issues",
        "Source": "https://github.com/yourusername/jan",
        "Documentation": "https://github.com/yourusername/jan/blob/main/README.md",
    },
)
