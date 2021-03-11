import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-YOUR-USERNAME-HERE",
    version="0.0.1",
    author="Ray Gomez",
    author_email="codenomad@gmail.com",
    description="A library of wrappers meant to help with QA.",
    install_requires=[
        "paramiko>=2.7.2",
        "requests>=2.25.0"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elibs/epython",
    project_urls={
        "Bug Tracker": "https://github.com/elibs/epython/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
