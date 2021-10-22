from setuptools import setup, find_packages
with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read()

with open("VERSION", "r") as f:
    version = f.read()

setup(
    name = "cookiecache",
    version = version,
    author = "PatH",
    author_email = "pypi_cookiecache@tofile.dev",
    license = "MIT",
    description = "Simplify getting and storing cookies from the browser to use in Python",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pathtofile/cookiecache",
    py_modules = ["cookiecache"],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = """
        [console_scripts]
        cookiecache=cookiecache.cookiecache:main
    """
)
