import setuptools
from setuptools import setup, find_packages
setup(
    name='afron_canbus',
    version='0.1.0',
    author="Uri Rotshtein",
    author_email="rotshtein@gmail.com",
    url="https://github.com/RogatY/Afron-Canbus.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    'afron-common>=0.1.0',
    'python-can>=3.3.3',
    'dataclasses-json>=0.5.2',
    'pigpio-pwm>=1.0',
    'getkey>=0.6.5'
    ]
)