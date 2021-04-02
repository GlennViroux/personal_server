# Personal Server Project

This repository contains code for a personal server powering the dynamical parts of my [website](https://www.glennviroux.com). I.e., it consists of the following parts:

## GNSS coverage tool

A tool for calculating the position of GNSS satellites, while also calculating which IGS stations are in view by which satellites at all times. At the moment, the four global GNSS networks (GPS, Galileo, Glonass and BeiDou) are supported.

Everything for this utility is launched using the main.py file.

## Convolutional Neural Network music genre classifier

A CNN, trained to classify audio samples in one of ten music genres: blues, classical, country, disco, hiphop, jazz, metal, pop, reggae or rock. The CNN is based on the Mel Spectogram of the provided audio sample.

## NASA APOD service

A simple service storing NASA's Astronomy Picture of the Day, together with it's summary. A simple API then provides the picture and summary for the requested day.
