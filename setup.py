from setuptools import find_packages, setup

VERSION = '0.1.9'

distribution = setup(
    name="txghserf",
    version=VERSION,
    maintainer='Adi Roiban',
    maintainer_email='adi.roiban@chevah.com',
    license='BSD 3-Clause',
    platforms='any',
    description="Simple server to listen for GitHub repo hooks.",
    long_description=open('README.rst').read(),
    url='https://github.com/chevah/txghserf',
    packages=find_packages('.'),
    package_data={
        'txghserf': [
            'static/*.html',
            'static/js/*.js',
            'static/css/*.css',
            ]
        },
    install_requires=[
        'klein',
        'twisted',
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    )
