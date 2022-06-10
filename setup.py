from setuptools import setup, find_packages
import pathlib

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

here = pathlib.Path(__file__).parent.resolve()
install_requires = (here / "requirements.txt").read_text(encoding="utf-8").splitlines()

setup(
    name="bgcar",
    version="0.0.1",
    author="simonkeyd",
    author_email="simon.kheng1337@gmail.com",
    license="GNU GPLv3",
    description="Baldur's Gate Computer Assisted Reroll for easy character high ability scores roll",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/simonkeyd/bgcar",
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["bgcar=bgcar.cli:main"],
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.4",
)
