from setuptools import setup, find_packages

setup(
    name="iaacompiler",
    version="1.0",
    packages=find_packages(),
    author="PAPERWAIT_rl",
    description="IAA Compiler module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
