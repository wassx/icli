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
        # Add dependencies here
        # 'pyicloud',
        # 'requests',
    ],
    python_requires='>=3.6',
)