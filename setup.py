from setuptools import setup
import io

with io.open('README.rst', encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="NooLite_F",
    packages=["NooLite_F", "NooLite_F.MTRF64"],
    version="0.0.9",
    license="MIT License",
    description="Module to work with NooLite/NooLite-F modules via MTRF-64-USB adapter",
    long_description=long_description,
    author="Sergey Prytkov",
    author_email="sergej.prytkov@gmail.com",
    url="https://github.com/SergejPr/NooLite-F",
    keywords="noolite noolite-f noolitef",
    install_requires=["pyserial"],
    platforms="any",
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
