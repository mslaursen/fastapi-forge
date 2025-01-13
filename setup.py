from setuptools import setup, find_packages


setup(
    name="fastapi-forge",
    version="0.1.4",
    packages=find_packages(),
    package_data={"fastapi_forge": ["static/*", "template/*"]},
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
