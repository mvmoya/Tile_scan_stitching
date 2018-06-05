# Tile_scan_stitching

Takes a rectangular tiled image and returns an image with duplicate pixels from 'seams' removed.
Seams sizes are established either manually or automatically
Automatic seam definition is currently for the very specific use case found in our lab. Acquired image resolution/magnification combinations yield consistent seam heights and widths in our use case, so a predetermined number of pixels are removed from the tile edges. Again, this suits a very particular use case.
Because adjacent tiles (and duplicate pixels within the resulting seam) do not appear to EXACTLY share pixel values, this was the quickest way to handle the stitching without searching for duplicated pixels in the image. Again, that is true in this particular case.

Manually setting the seam height and widths is the ideal way to go if you have consistent sized seams across your tile scan. The program offers you the option to preview the set seam sizes before accepting and running the stitching. Horizontal and vertical seams are set independently.
An image montage containing the tiles with the seams "cropped" away is returned.
