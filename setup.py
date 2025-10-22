import codecs
import os.path

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

setup(
    name='netbox-qrcode',
    version='0.0.19',
    description='QR Code generation for netbox objects',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/netbox-community/netbox-qrcode',
    author='Nikolay Yuzefovich',
    author_email='mgk.kolek@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    min_version='4.3.0',
    max_version='4.3.99',
    package_data={
        '': ['*.ttf'],
        '': ['*.html'],
    },
    install_requires=[
        'qrcode',
        'Pillow'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ]
)
