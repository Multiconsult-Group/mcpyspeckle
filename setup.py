import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcpyspeckle",
    version="0.0.1",
    author="Morten Engen",
    author_email="morten.engen@multiconsult.no",
    description="Extension to the pyspeckle module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Multiconsult-Group/mcpyspeckle",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)