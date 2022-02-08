from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tello',
    packages=['tello'],
    version='0.0.1',
    author="Harley Lara",
    author_email="contact@harleylara.com",
    description='Tello drones python wrapper ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
