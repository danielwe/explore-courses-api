import setuptools

setuptools.setup(
    name="explorecourses",
    version="2.0.0",
    url="https://github.com/danielwe/explore-courses-api",
    author="Jeremy Ephron, Daniel Wennberg",
    author_email="jeremye@stanford.edu, daniel.wennberg@gmail.com",
    description="A Python API for Stanford Explore Courses",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests>=2'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
