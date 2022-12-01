from setuptools import find_packages, setup
from pkg_resources import parse_requirements

if __name__ == '__main__':
    setup(
        name='translation',
        version='0.1',
        packages=find_packages("."),
        #install_requires=list(map(str, parse_requirements(open("requirements.txt")))),
    )