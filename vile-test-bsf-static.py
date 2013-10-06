#!/usr/bin/env python

# Author: Ryan Balsdon <ryanbalsdon@gmail.com>
#
# I dedicate any and all copyright interest in this software to the
# public domain. I make this dedication for the benefit of the public at
# large and to the detriment of my heirs and successors. I intend this
# dedication to be an overt act of relinquishment in perpetuity of all
# present and future rights to this software under copyright law.

import vile

bsfLogo = vile.VileFrame()
bsfLogo.loadTGA("bsf.tga")

rows, cols = vile.getScreenSize()
bsfLogo.render(rows, cols)