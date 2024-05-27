#!/bin/bash
mkdir worksheets

cd macropad/worksheet/
# This is a bit of a cheat, there's probably a better way of doing it.
cp -r ../../worksheet-components/* ./
make

cd ../../worksheets
cp ../macropad/worksheet/worksheet.pdf ./macropad.pdf
