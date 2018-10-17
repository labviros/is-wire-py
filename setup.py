from setuptools import setup, find_packages

setup(
    name='is_wire',
    version='1.1.3',
    description='',
    url='http://github.com/labviros/is-wire-py',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    install_requires=[
        'colorlog==3.1.4',
        'amqp==2.3.2',
        'enum34==1.1.6',
        'protobuf==3.6.0',
        'is-opencensus>=0.1.5.3',
        'prometheus-client==0.3.1',
    ]
    # change 'is-opencensus' to 'opencensus' when pull request accepted
)
