
from __future__ import absolute_import

import os
from glob import glob

from setuptools import find_packages, setup


def read(fname):
    """
    Args:
        fname:
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Declare minimal set for installation
required_packages = [
    #"boto3>=1.20.21,<2.0",
    #"pandas",
]

setup(
    name="synthdog",
    version="0.0.1",
    description="Customized synthdog package from donut-python project",
    long_description_content_type="text/markdown",
    long_description=read('README.md'),
    packages=find_packages(
        exclude=[
            "*.ipynb",
            "misc",
            "outputs",
            "README.md",
            "LICENCE",
        ]
    ),
    #py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob("aws_feature_store/*.py")],
    include_package_data=True,
    author="ML Team",
    url="https://github.com/bilykigor/synthdog.git",
    license="Apache License 2.0",
    keywords="synthdog donut",
    python_requires=">= 3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=required_packages
)
