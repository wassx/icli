from setuptools import setup, find_packages

setup(
    name="icli",
    version="0.1.0",
    description="A command-line interface for iCloud services",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'icli=main:main',
        ],
    },
    install_requires=[
        'pyicloud>=2.4.1',
        'requests>=2.31.0',
        'keyring>=24.2.0',
    ],
    python_requires='>=3.6',
)