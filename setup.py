import setuptools

install_requires = [
    'Pillow==8.3.1',
    'numpy~=1.21.2',
]
setuptools.setup(
    name="RectangleCropper",
    version="1.0.0",
    license='MIT',
    author="Shinyook Lee <tlsdbr97@gmail.com>",
    author_email="tlsdbr97@gmail.com",
    description="Crop image to rectangle",
    long_description=open('README.md').read(),
    url="https://github.com/leeshinyook/RectangleCropper",
    packages=setuptools.find_packages(),
    install_requires = install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3',
)