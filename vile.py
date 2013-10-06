#!/usr/bin/env python

# Author: Ryan Balsdon <ryanbalsdon@gmail.com>
#
# I dedicate any and all copyright interest in this software to the
# public domain. I make this dedication for the benefit of the public at
# large and to the detriment of my heirs and successors. I intend this
# dedication to be an overt act of relinquishment in perpetuity of all
# present and future rights to this software under copyright law.
#
# Vile is a simple ASCII-art generator that uses VT100 commands to draw
#to a terminal. On Linux, the standard terminals are all fast enough to
#do real-time animations but the default OSX terminal is a bit too slow.

import os, sys, time, math

def setCursorPos(x,y):
    """Sends the VT100 terminal command to set the cursor's position."""
    sys.stdout.write("%c[%d;%df" % (0x1B,y,x))

def getScreenSize():
    """Asks for the terminal dimensions using the 'stty size' system command"""
    rows, columns = os.popen('stty size', 'r').read().split()
    return (int(rows), int(columns))

def asciiStrength(power):
    """Converts a float (0.0 to 1.0) to an ASCII character, based on the ASCII character's 
    brightness. Different fonts will have different brightnesses so this function may have 
    to be modified to suit different environments"""
    charSet = [' ','.','`',':','\'','-',',',';','"','y','!','*','_','\\','/','^','r','v','m','c','x','+','|','(',')','?','<','>','=','t', \
		's','Y','7','z','T','L','j','n','u','f','o','i','l','V','k','e','X','J','}','{','1',']','[','a','h','C','w','4','q','d','A', \
		'b','Z','2','p','I','F','K','P','U','%','3','S','O','G','g','H','&','6','0','D','5','9','N','R','E','8','Q','M','#','W','B', \
		'$','@']
    index = int(power*(len(charSet)-1))
    return charSet[index]
        
class VileFrame:
    """Stores an ASCII art image and provides some functions for modifying and loading one"""
    
    def __init__(self):
        self.rows = 24
        self.columns = 80
    	self.data = [[0.0]*self.rows for x in xrange(self.columns)]

    def render(self, screenHeight, screenWidth):
        """Displays the loaded grey-scale image as an ASCII art image on the terminal. Scales the image to the given screen size in letters."""
    	for y in range(screenHeight):
    		setCursorPos(0,y+1)
    		for x in range(screenWidth):
    			sys.stdout.write(asciiStrength(self.data[int(1.0*x/screenWidth*self.columns)][int(1.0*y/screenHeight*self.rows)]))
        sys.stdout.flush()

    def loadTGA(self, image):
        """Loads an image file and converts to grey-scale
        Must be a targa (TGA) file and be RGBA, not RGB format
        """
    	f = open(image, "rb")
    	byte = f.read(12)
    	byte = f.read(2)
    	self.columns = ord(byte[0])+256*ord(byte[1])
    	#print "Columns:"+str(columns)+" "+str(int(ord(byte[0])))+" "+str(int(ord(byte[1])))
    	byte = f.read(2)
    	self.rows = ord(byte[0])+256*ord(byte[1])
    	#print "Rows:"+str(rows)+" "+str(int(ord(byte[0])))+" "+str(int(ord(byte[1])))
    	self.data = [[0.0]*self.rows for x in xrange(self.columns)]
    	byte = f.read(2)
    	for y in range(self.rows-1,-1,-1):
    		for x in range(self.columns):
    			byte = f.read(4)
    			#print "X: "+str(x)+", Y: "+str(y)
    			self.data[x][y] = 1.0-(ord(byte[0])+ord(byte[1])+ord(byte[2])+0*ord(byte[3]))/255.0/3.0
    			#print "Pixel: "+str(data[x][y])

    def darken(self, scale):
        """Multiplies the saved grey-scale image by the given scale (0.0 is white)"""
    	for y in range(self.rows):
    		for x in range(self.columns):
    			self.data[x][y] = scale*self.data[x][y]

    def scale(self, scale):
        """Scales and centers the image."""
    	scaledData = [[0.0]*self.rows for x in xrange(self.columns)]
    	if scale == 0.0:
            self.data = scaledData
            return
    	invScale = 1/scale
    	#Scale
    	for y in range(self.rows):
    		if int(y*invScale) < self.rows:
    			for x in range(self.columns):
    				if int(x*invScale) < self.columns:
    					scaledData[x][y] = self.data[int(x*invScale)][int(y*invScale)]
    	#Shift
        self.data = [[0.0]*self.rows for x in xrange(self.columns)]
    	shiftY = int(-0.5*(1.0-scale)*self.columns)
    	shiftX = int(-0.5*(1.0-scale)*self.rows)
    	for y in range(self.rows):
    		if (y+shiftY) < self.rows and (y+shiftY) >= 0:
    			for x in range(self.columns):
    				if (x+shiftX) < self.columns and (x+shiftX) >= 0:
    					self.data[x][y] = scaledData[x+shiftX][y+shiftY]
                        
    def translate(self, shiftX, shiftY):
        """Shifts the image by the given number of pixels. This is image pixels, not screen pixels"""
        shiftX = int(shiftX)
        shiftY = int(shiftY)
        data = [[0.0]*self.rows for x in xrange(self.columns)]
    	for y in range(self.rows):
    		if (y+shiftY) < self.rows and (y+shiftY) >= 0:
    			for x in range(self.columns):
    				if (x-shiftX) < self.columns and (x-shiftX) >= 0:
    					data[x][y] = self.data[int(x-shiftX)][int(y+shiftY)]
        self.data = data

    def copy(self):
        """Returns a deep copy of this VileFrame. Useful for animating a frame without modifying the original."""
        copy = VileFrame()
        copy.rows = self.rows
        copy.columns = self.columns
    	copy.data = [[0.0]*copy.rows for x in xrange(copy.columns)]
    	for x in range(copy.columns):
    		copy.data[x] = self.data[x][:]
    	return copy

    #doesn't add colours, it adds layers
    def add(self, frame):
        """Combines two frames by layering the given frame on top of self.
        Self's frame will only show through when the given layer is white.
        """
    	rows = self.rows
    	if frame.rows<rows:
    		rows = frame.rows
    	cols = self.columns
    	if frame.columns<cols:
    		cols = frame.columns
    	newData = [[0.0]*rows for x in xrange(cols)]
    	rowScale1 = 1.0*self.rows/rows
    	colScale1 = 1.0*self.columns/cols
    	rowScale2 = 1.0*frame.rows/rows
    	colScale2 = 1.0*frame.columns/cols
    	for y in range(rows):
    		for x in range(cols):
    			newData[x][y] = self.data[int(x*colScale1)][int(y*rowScale1)]
    			if frame.data[int(x*colScale2)][int(y*rowScale2)] > 0.01:
                    #if the frame isn't transparent/white, show it
    				newData[x][y] = frame.data[int(x*colScale2)][int(y*rowScale2)]
    	self.data = newData
    	self.rows = len(newData[0])
    	self.columns = len(newData)
        

