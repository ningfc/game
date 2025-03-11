#!/bin/bash

pyinstaller -y --clean --windowed --icon simple_wave_reflection.png --add-data "simple_wave_reflection.png:." --name Waves simple_wave_reflection.py