#!/bin/bash

mkdir cleaned
mkdir origin
python extractSeries.py
python extractData.py
