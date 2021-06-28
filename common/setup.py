from setuptools import setup, find_packages
setup(
    name='hlc/common',
    version='0.1.1',
    author="Uri Rotshtein",
    author_email="rotshtein@gmail.com",
    url="https://github.com/RogatY/Afron-Common.git",
    packages=['src'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'paho-mqtt>=1.5.1',
    ]
)
