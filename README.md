# Utilities

A bunch of (mostly python) utillities, well I say a bunch, but that'll come in time.

## Palette
Creates a palette png from an image.
Takes a number file argument and dumps an image with the most dominant colours in the working directory for each file.

No error checking, no security, filename is same as given basename with .png appended.

Uses colorthief library and takes anything PIL accepts on your system.
