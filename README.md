<p align="center"><img src="static/logo.png" alt="LiveWires" width=400></p>

# LiveWires Electronics Repo

Welcome to the LiveWires electronics repo. Eventually hopefully all the project information will be on here. For now it's just the new projects since this has been created.

Worksheets can be downloaded by finding the latest release (check the right hand bar on github) and downloading the worksheets.zip file

## Macro Pad

This is the LiveWires Macro Pad, an 8-key macro pad based on a Raspberry Pi Pico and cherry switches. It has up to 16 configurable pages of keys, and runs CircuitPython.

[Click here to find out more](macropad/README.md)

## Analogue Synthesiser

This is the LiveWires analogue synthesiser, a musical instrument with 5 octaves of output, a 1 octave keyboard, 8 control dials and entirely analogue processing of a digitally produced wave.

[Click here to find out more](synth/README.md)


## Release Process

Create a draft release by going to `Releases > Draft a new release` in github.

Set the title accordingly, and change the "Tag" to create a new tag, vX.Y, where X.Y must be larger than the previous release. Describe the reason for doing the release in the description.

Download the worksheets.zip artifact from a build run with the desired changes, and upload them to the release. If no build has been performed in the last 90 days, you will need to manually trigger a new build. Go to the actions page, click on the action on the left hand side titled "Build LaTeX Documents" and then click the "Run Workflow" button
