from setuptools import setup, find_packages

setup(
    name='is_wire',
    version='1.2.0',
    description='',
    url='http://github.com/labviros/is-wire-py',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    install_requires=[
        'colorlog==3.1.4',
        'amqp==2.4.2',
        'enum34==1.1.6',
        'protobuf==3.6.0',
        'opencensus==0.5.0',
        'prometheus-client==0.3.1',
    ]
)
