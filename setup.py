from setuptools import setup, find_packages

setup(
    name='is_wire',
    version='1.0.5.1',
    description='',
    url='http://github.com/labviros/is-wire-py',
    author='labviros',
    license='MIT',
    packages=[ 'is_wire', 'is_wire.core', 'is_wire.rpc' ],
    zip_safe=False,
    install_requires=['pika==0.12.0', 'termcolor', 'is-msgs', 'is-opencensus']
    # change 'is-opencensus' to 'opencensus' when pull request accepted
)
