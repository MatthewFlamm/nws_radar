from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "nws_radar",
    version = "0.0.2",
    license='MIT License',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MatthewFlamm/nws_radar',
    author = "Matthew Flamm",
    author_email = "matthewflamm0@gmail.com",
    description = "Python library to get NWS radar images",
    packages=['nws_radar'],
    include_package_data=True,
    install_requires=[
        'requests',
        'BeautifulSoup4',
        'Pillow'
        ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"],
)
