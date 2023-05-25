from setuptools import find_packages, setup

setup(
    name="BallMotion",
    version="0.1.0",
    description="3D tracking and motion analysis of a ball",
    author="Florian Beck, Franz Ostler, Jan Duchscherer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    console_scripts=[
        # "ballmotion=main:main",
    ],
    install_requires=[
        "numpy",
        "opencv-python",
        # 'scipy',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
