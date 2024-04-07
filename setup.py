from setuptools import setup

setup(
    name="telescope",
    version="0.0.1",
    description="GoTo Altazimuth Telescope Engineering Capstone Project",
    url="https://github.com/Mac-Coleman/EGR-385-Telescope-Mount",
    author="Mac Coleman",
    author_email="williamcormaccoleman@gmail.com",
    license="none",
    packages=["telescope"],
    install_requires=[
        "RPi.GPIO",
        "adafruit-circuitpython-gps",
        "adafruit-circuitpython-mmc56x3",
        "adafruit-circuitpython-adxl34x",
        "adafruit-circuitpython-seesaw",
        "pandas",
        "magnetismi",
        "smbus2",
        "skyfield",
        "rpi-hardware-pwm",
        "keyboard"
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3"
    ]
)
