from setuptools import setup, find_packages


setup(
    name="fastapi-forge",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "uvicorn",
        "pydantic",
        "cookiecutter",
        "click",
        "nicegui",
    ],
    entry_points={
        "console_scripts": ["fastapi-forge = fastapi_forge:main"],
    },
    include_package_data=True,
)
