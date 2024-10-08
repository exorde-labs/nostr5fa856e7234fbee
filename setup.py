from setuptools import find_packages, setup

setup(
    name="nostr5fa856e7234fbee",
    version="0.0.8",
    packages=find_packages(),
    install_requires=[
        "exorde_data",
        "aiohttp",
        "beautifulsoup4>=4.11",
        "pynostr>=0.6.2",
        "nest_asyncio==1.5.6",
        "bech32==1.2.0"
    ],
    extras_require={"dev": ["pytest", "pytest-cov", "pytest-asyncio"]},
)
