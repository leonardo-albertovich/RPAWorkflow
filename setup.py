import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="leonardo-albertovich", # Replace with your own username
    version="0.0.1",
    author="leonardo-albertovich",
    author_email="l_alminana@yahoo.com.ar",
    description="A simple RPA workflow handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonardo-albertovich/rpaworkflow",
    packages=setuptools.find_packages(include=['RPAWorkflow*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)