# SLS-M-Square-Specimen-Slicer
This is a bespoke GCODE writer for a bespoke SLS/M Powder Bed 3D Printer for printing 2D square specimens. 

The primary feature of the writer is to vary hatch spacing (Overlap) and scan velocity within a single layer.

The Slicer uses an interlaced scan strategy to mitigate thermal warpage due to poor or absent bed adhesion.

The Slicer is parameterized for a layout as follows in the figure below, only the squares_max_x and squares_min_y need be modified for different print bed formats.

All dimensions are in mm.

![image](https://github.com/skbrownlee/SLS-M-Square-Specimen-Slicer/assets/70294121/54da2773-aa10-48bc-9ca1-754692e867e7)

