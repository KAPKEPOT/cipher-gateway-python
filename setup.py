from setuptools import setup, find_packages

setup(
    name="cipher-gateway",
    version="1.0.0",
    description="Python SDK for the Cipher MT5 Gateway",
    author="CipherBridge",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.24.0",
        "websockets>=11.0",
    ],
)
