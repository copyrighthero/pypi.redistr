# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

# import required setup libraries
from setuptools import setup, find_packages
from codecs import open
from os import path

# import library for metadata
from redistr import __author__, __license__, __version__

# project absolute directory
DIRECTORY = path.abspath(path.dirname(__file__))

# project readme file content
with open(
  path.join(DIRECTORY, 'README.rst'), encoding = 'UTF8'
) as file_descriptor:
  PROJECT_README = file_descriptor.read()

# project required dependencies
with open(
  path.join(DIRECTORY, 'requirements.txt'), encoding = 'UTF8'
) as file_descriptor:
  REQUIREMENTS = tuple(line for line in file_descriptor if line)

# project setup parameters
setup(
  name = 'Redistr',
  version = __version__,
  description = 'Redis backed Python data structure interface.',
  long_description = PROJECT_README,
  url = 'https://www.github.com/copyrighthero/Redistr',
  download_url = 'https://www.github.com/copyrighthero/Redistr',
  author = __author__,
  author_email = 'copyrighthero@gmail.com',
  license = __license__,
  classifiers = (
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only'
  ),
  keywords = 'Redis Remote Data-structure Multi-processing',
  # py_modules = ("Redistr", ),
  packages = find_packages(exclude = ()),
  install_requires = REQUIREMENTS,
  package_data = {},
  data_files = (),
  entry_points = {},
  project_urls = {
    'Source': 'https://www.github.com/copyrighthero/Redistr'
  }
)
