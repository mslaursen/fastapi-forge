from setuptools import setup, find_packages


setup(
    name="fastapi-forge",
    version="0.1.14",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "cookiecutter",
        "click",
    ],
    entry_points={
        "console_scripts": ["fastapi-forge = fastapi_forge:main"],
    },
    include_package_data=True,
)
