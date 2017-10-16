from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'LICENSE.txt'), encoding='utf-8') as f:
    license_description = f.read()

setup(
    name='NooLiteF',
    packages=['NooLiteF'],
    version='0.0.4',
    license=license_description,
    description='Module to work with NooLiteF (MTRF-64-USB)',
    long_description=long_description,
    author='Sergey Prytkov',
    author_email='sergej.prytkov@gmail.com',
    url='https://github.com/SergejPr/NooLite-F',
    keywords=['noolite', 'noolite-f', 'noolitef'],
    install_requires=['pyserial'],
    platforms='osx, posix, linux, windows',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ]
)
