from distutils.core import setup
setup(
  name='NooLiteF',
  packages=['NooLiteF'],
  version='0.0.1',
  description='Module to work with NooLiteF (MRTF-64-USB)',
  author='Sergey Prytkov',
  author_email='sergej.prytkov@gmail.com',
  license='MIT',
  url='https://github.com/SergejPr/NooLite-F',
  download_url='https://github.com/SergejPr/NooLite-F/archive/0.1.tar.gz',
  keywords=['noolite', 'noolite-f', 'noolitef'],
  install_requires=['pyserial'],
  python_requires='>=3',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Home Automation",
    "Topic :: System :: Hardware",
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)
