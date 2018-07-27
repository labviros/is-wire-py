from setuptools import setup, find_packages

setup(
    name='is_wire',
    version='1.1.0',
    description='',
    url='http://github.com/labviros/is-wire-py',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    install_requires=[
        'colorlog==3.1.4',
        'librabbitmq==2.0.0',
        'enum34==1.1.6',
        'is-msgs',
        'is-opencensus',
    ]
    # change 'is-opencensus' to 'opencensus' when pull request accepted
)
