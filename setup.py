from setuptools import setup, find_packages

setup(
    name='Cardinal',
    version='3.0.0',
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        cardinal=cardinal.cli:cli
    ''',
)
