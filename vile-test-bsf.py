#!/usr/bin/env python

# Author: Ryan Balsdon <ryanbalsdon@gmail.com>
#
# I dedicate any and all copyright interest in this software to the
# public domain. I make this dedication for the benefit of the public at
# large and to the detriment of my heirs and successors. I intend this
# dedication to be an overt act of relinquishment in perpetuity of all
# present and future rights to this software under copyright law.

# Please keep in mind that these are the absolute worst shapes to be trying
#to do this on. It'll work best on simple, very high-contrast shapes where
#these are thin and detailed.

import vile, time, math

vileLogo = vile.VileFrame()
vileText = vile.VileFrame()
vileVignette = vile.VileFrame()
vileLogo.loadTGA("bsf-logo.tga")
vileText.loadTGA("bsf-text.tga")
vileVignette.loadTGA("vignette.tga")
vileVignette.darken(0.2)

def smoothMotion(percent):
    return math.sin(percent*math.pi/2.0)


rows, cols = vile.getScreenSize() #saving the screen size now because this function is too slow to run every frame
frameDelay = 1.0/60.0 # 30 fps is high enough for a splash screen
currentTime = 0.0
animationLength = 2.0

while (currentTime < animationLength):
    animationProgress = currentTime/animationLength
    
    #making copies of everything so I can modify the layers
    vignette = vileVignette.copy()
    logo = vileLogo.copy()
    text = vileText.copy()
    
    #animating
    vignette.darken(smoothMotion(animationProgress))
    logo.scale(smoothMotion(animationProgress))
    text.translate(cols*(1.0-smoothMotion(animationProgress)), 0.3*rows*(1.0-smoothMotion(animationProgress)))
    
    #layering the final image
    vileFrame = vignette
    vileFrame.add(logo)
    vileFrame.add(text)
    
    #finally, render
    vileFrame.render(rows, cols)
    
    #and wiat for next frame
    time.sleep(frameDelay) #does not take render time into account but I'm ok with that
    currentTime+=frameDelay