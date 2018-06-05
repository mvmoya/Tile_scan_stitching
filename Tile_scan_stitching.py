import ij.plugin as plugin
import ij.gui as gui
import ij.process
from ij import ImageStack
from ij import IJ
import ij.io.FileInfo as fileInfo

imp = IJ.getImage()
impProcessor = IJ.getProcessor()
impProcessor.setLineWidth(1)
impProcessor.setColor(25)
imp.setOverlay(gui.Overlay())
pixelHeight = round(imp.getLocalCalibration().pixelHeight, 4)
name = imp.getShortTitle().upper()
magnification = ''

if [x in name for x in ['5X', '10X', '20X', '40X', '63X', '100X']].count(True) == 1:
	window = gui.NonBlockingGenericDialog("Specify Tile Scan Properties")
	window.addMessage("What are the tile scan dimensions?")
	window.addNumericField('Height:  ', 2.0, 1)
	window.addNumericField('Width:  ', 3.0, 1)
	window.addCheckbox('Set seam sizes manually?   ', False)
	window.addCheckbox('Approve seams first?   ', True)
	window.showDialog()
	
	if window.wasCanceled():	
		raise Exception("Try Again")
		
	yTiles = window.getNextNumber()
	xTiles = window.getNextNumber()
	manually = window.getNextBoolean()
	approve = window.getNextBoolean()

else:
	window = gui.NonBlockingGenericDialog('Specify Tile Scan Properties')
	window.addMessage('What are the tile scan dimensions?')
	window.addNumericField('Height:  ', 2.0, 1)
	window.addNumericField('Width:  ', 3.0, 1)
	window.addChoice('Magnification:  ', ['5X', '10X', '20X', '40X', '63X', '100X'], '10X')
	window.addCheckbox('Set seam sizes manually?   ', False)
	window.addCheckbox('Approve seams first?   ', True)
	window.showDialog()
	
	if window.wasCanceled():	
		raise Exception('Try Again')
		
	yTiles = window.getNextNumber()
	xTiles = window.getNextNumber()
	magnification = window.getNextChoice()
	manually = window.getNextBoolean()
	approve = window.getNextBoolean()
	
if xTiles != xTiles or yTiles != yTiles:
    errorDialog = gui.NonBlockingGenericDialog('Error')
	errorDialog.addMessage('Dimensions should be expressed as valid integers')
	errorDialog.showDialog()
	raise ValueError('Dimensions should be expressed as valid integers')

imageHeight = imp.getFileInfo().height
tileHeight = imageHeight / yTiles
imageWidth = imp.getFileInfo().width
tileWidth = imageWidth / xTiles
seamOverlay = gui.Overlay()

if not manually:
	factor = pixelHeight / 0.3126 # This seems to be the smallest pixel value for our standard tile scans?
	
	if '10X' in name or magnification == '10X':
		seamHeight = 14 / factor
		seamWidth = 10 / factor
		
	elif '20X' in name or magnification == '20X':
		seamHeight = 12 / factor
		seamWidth = 0 / factor	
        
	#elif '40X' in name or magnification == '40X':
	#	pass
	#elif '60X' in name or magnification == '63X':
	#	pass
	#elif '100X' in name or magnification == '100X':
	#	pass
	
	elif '5X' in name or magnification == '5X':	
		seamHeight = 24 / factor
		seamWidth = 0 / factor
	
	else:
		errorDialog = gui.NonBlockingGenericDialog('Oops, Sorry!')
		errorDialog.addMessage("She hasn't added this functionality yet!")
		errorDialog.showDialog()
		raise Exception('Check back later! GTFO')

	for i in range(yTiles - 1):
		hSeam = gui.Roi(0, tileHeight + tileHeight * i, imageWidth, seamHeight)
		seamOverlay.add(hSeam)

		for j in range(xTiles - 1):	
			vSeam = gui.Roi(tileWidth + tileWidth * j, 0, seamWidth, imageHeight)
			seamOverlay.add(vSeam)

	imp.setOverlay(seamOverlay)
	window = gui.NonBlockingGenericDialog("Approve the seams")
	window.addMessage("Zoom in and check that the seams\r\nare in the correct places.\r\nThen click OK.\r\nIf wrong, click Cancel.")
	window.showDialog()
	
	if window.wasCanceled():	
		manually = True

while manually:
	try:
		seamHeight = float(seamHeight)
		seamWidth = float(seamWidth)
		
	except:
		seamHeight = 7.0
		seamWidth = 0.0
	
	window = gui.NonBlockingGenericDialog('Set Seam Sizes Manually')
	window.addMessage('Set the sizes of the seams in pixels')
	window.addNumericField('Horizontal seam (px):   ', seamHeight, 1)
	window.addNumericField('Vertical seam (px):   ', seamWidth, 1)
	window.showDialog()
	
	if window.wasCanceled():	
		raise Exception('GTFO')
		break
		
	seamHeight = window.getNextNumber()
	seamWidth = window.getNextNumber()
	
	if seamHeight != seamHeight or seamWidth != seamWidth:	
		errorDialog = gui.NonBlockingGenericDialog()
		errorDialog.addMessage('Seam sizes must be valid integers')
		errorDialog.showDialog()
		raise ValueError('Seam sizes must be valid integers')
		break

	imp.setOverlay(gui.Overlay())
	seamOverlay = gui.Overlay()
	
	for i in range(yTiles - 1):
		hSeam = gui.Roi(0, tileHeight + tileHeight * i, imageWidth, seamHeight)
		seamOverlay.add(hSeam)

		for j in range(xTiles - 1):	
			vSeam = gui.Roi(tileWidth + tileWidth * j, 0, seamWidth, imageHeight)
			seamOverlay.add(vSeam)

	imp.setOverlay(seamOverlay)
	window = gui.NonBlockingGenericDialog("Approve the seams")
	window.addMessage("Zoom in and check that the seams\r\nare in the correct places.\r\nThen click OK.\r\nIf wrong, click Cancel.")
	window.showDialog()
	
	if window.wasCanceled():	
		continue

	elif window.wasOKed():		
		break

for i in range(yTiles):
	if i == 0:	
		yMin = seamHeight
		
	else:	
		yMin = (tileHeight * i) + seamHeight
	
	yMax = tileHeight - seamHeight
    
	for j in range(xTiles):			
		if j == 0:		
			xMin = seamWidth
			
		else:		
			xMin = (tileWidth * j) + seamWidth
		
		xMax = tileWidth - seamWidth

		if i == 0 and j == 0:		
			finalStack = ImageStack(int(xMax), int(yMax))
		
		tempRoi = gui.Roi(xMin, yMin, xMax, yMax)
		roiImage = imp.setRoi(tempRoi, False)
		duped = imp.duplicate()
		dupedProcessor = duped.getProcessor()
		finalStack.addSlice(dupedProcessor)

stackImage = ij.ImagePlus('Stack', finalStack)
montageImage = plugin.MontageMaker().makeMontage2(stackImage, int(xTiles), int(yTiles), 1.0, 1, int(xTiles*yTiles), 1, 0, False)
montageImage.setTitle('Stitching Result')
montageImage.show()
