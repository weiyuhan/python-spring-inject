import setuptools

setuptools.setup(
    name="pyspring-inject",
    version="0.0.1",
    author="Yuhan Wei",
    author_email="weiyuhan@pku.edu.cn",
    description="Springboot-like Dependency Injection Framework for Python",
    url="https://github.com/weiyuhan/python-spring-inject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        'pyhocon>=0.3.60',
        'inject==5.0.0',
    ]
)
