from distutils.core import setup

setup(
    name='Schedaddle',
    version='0.1.0',
    author='David Davis',
    author_email='davisd@davisd.com',
    packages=['schedaddle',],
    url='http://www.davisd.com/projects/python-schedaddle',
    data_files=[('.',['LICENSE'])],
    license='LICENSE',
    description='Schedaddle is a python package for getting dates and times on'\
    ' scheduled intervals',
    long_description=open('README').read(),
)
