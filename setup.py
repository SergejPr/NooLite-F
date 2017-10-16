from setuptools import setup

import io


with io.open('README.rst', encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with io.open('LICENSE.txt', encoding="utf-8") as license_file:
    license_description = license_file.read()

setup(
    name="NooLite_F",
    packages=["NooLite_F"],
    version="0.0.1",
    license=license_description,
    description="Module to work with NooLite_F (MTRF-64-USB)",
    long_description=long_description,
    author="Sergey Prytkov",
    author_email="sergej.prytkov@gmail.com",
    url="https://github.com/SergejPr/NooLite_F",
    keywords="noolite noolite-f noolitef",
    install_requires=["pyserial"],
    platforms="osx, posix, linux, windows",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ]
)
