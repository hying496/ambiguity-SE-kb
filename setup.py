"""
项目安装脚本
"""
from setuptools import setup, find_packages

setup(
    name="ambiguity-se-kb",
    version="0.1.0",
    description="中文软件工程消歧知识库",
    author="消歧知识库团队",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
        "pymilvus>=2.3.0",
        "jsonschema>=4.17.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
)


