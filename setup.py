# coding: utf-8
exec(open('hexconnector/version.py').read())


from setuptools import setup

def next_version():
    _v = __version__.split('.')
    _v[-1] = str(int(_v[-1]) + 1)
    return '.'.join(_v)

def read_file(f):
    try:
        with open(f, 'r') as _file:
            return _file.read()
    except Exception as e:
        return ''

setup(
    name='hexconnector',
    version=__version__,
    url='https://github.com/laco/python-hexconnector/',
    download_url='https://github.com/laco/python-hexconnector/tarball/' + __version__,
    license='BSD',
    author='László Andrási',
    author_email='mail@laszloandrasi.com',
    description='Python Hexagonal Architecture with Dynamic Module Loading',
    long_description=read_file('README.md') + '\n\n',
    packages=['hexconnector'],
    include_package_data=True,
    package_data = {
        'hexconnector': ['LICENSE', 'README.md']},
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
