###################
# 
# This file is part of geField package.
# Copyright 2014 Ivan Del Mastro <info [a-t] adventure2italy.com>
# Version	1.0.0
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
# 
# * @license    GNU/GPL - MIT, see above
###################

from PIL import Image
import os
from django.utils.translation import ugettext_lazy as _

cardinals = {
    'N': 'compass_N.png',
    'NE': 'compass_NE.png',
    'E': 'compass_E.png',
    'SE': 'compass_SE.png',
    'S': 'compass_S.png',
    'SW': 'compass_SW.png',
    'W': 'compass_W.png',
    'NW': 'compass_NW.png',
    }

shadows = {
    'N': 'compass_y_N.png',
    'NE': 'compass_y_NE.png',
    'E': 'compass_y_E.png',
    'SE': 'compass_y_SE.png',
    'S': 'compass_y_S.png',
    'SW': 'compass_y_SW.png',
    'W': 'compass_y_W.png',
    'NW': 'compass_y_NW.png',
}
COMPASS_espositions_CHOICE = (
        (u'N', _(u'Nord' )),
        (u'NE', _(u'Nord Est' )),
        (u'E', _(u'Est')),
        (u'SE', _(u'Sud Est' )),
        (u'S', _(u'Sud')),
        (u'SW', _(u'Sud West' )),
        (u'W', _(u'West' )),
        (u'NW', _(u'Nord West' )),
        )
def lenField():
    l = []
    for k,v in COMPASS_espositions_CHOICE:
        l.append(k)
    return len(','.join(l))
    
BACKGROUND_IMG = 'compass_bg.png'   # il nome dell'imagine background
BACKGROUND_DIR = 'geowork/images'   # la directory dove sono le immagini base da comporre
EXTENSION_NAME = '_compass.png'     # estensione del file immagine genrato da aggiungere a 'path' 

class Img(object):
    def __init__(self, path, esposition, width, thumbnail):
        compass_file_name, background_size = createCompass(path, esposition, width)
        self.compass_file_name = compass_file_name
        self.background_size_w = background_size[0]
        self.background_size_h = background_size[1]
    
    @property
    def path_name(self):
        return self.compass_file_name.replace('\\','/')
    
    @property
    def w(self):
        return self.background_size_w
        
    @property    
    def h(self):
        return self.background_size_h
        
class Compass(object):
    def __init__(self, esposition = [], path = "", prefix_name = "prefix_", width=250, thumbnail = 1.0):
        self.esposition = esposition
        self.path = path
        self.prefix_name = prefix_name
        self.width = width   
        self.thumbnail = thumbnail
    
    @property
    def getEsposition(self):
        return u", ".join(self.esposition)
        
    @property
    def image(self):
        return Img(self.path, self.esposition, self.width, self.thumbnail)
    
    def __len__(self): 
        return len(self.esposition)
    
    def __iter__(self):
        return self.esposition.__iter__()
        
    def __str__(self):
        return "%s" % Compass.__name__
    def __unicode__(self):
        return u"%s" % self.__str__()
        
def createCompass(path, espositions = [], width=250):
    show, save = False, True
    # path include il nome del file.
    # la funzione createCompass aggiunge in automatico
    # l'estenzione _compass.png
    
    # in caso di espositions = [] genera solo l'immagine file background
    
    name = "" #os.path.basename(path)
    dir_name = path #os.path.dirname(path)
    
    
    EXP = "_EXP_%s_EXP_%s" % ("-".join(espositions), width)
    compass_file_name = name + EXP + EXTENSION_NAME
    
    # se il file esiste, non genera nulla
    # ritorna il file e risparmia risorse
    if os.path.isfile(os.path.join(dir_name, compass_file_name)):
        im = Image.open( os.path.join(dir_name, compass_file_name), 'r' )
        return os.path.join(dir_name, compass_file_name), im.size
    else:
        pass
    
    background=Image.open( os.path.join(BACKGROUND_DIR, BACKGROUND_IMG), 'r' )
    w,h = background.size

    # aggiunge solo le immagini se presenti nei valori predefiniti
    for e in espositions:
        if cardinals.has_key(e):
            img=Image.open( os.path.join(BACKGROUND_DIR,cardinals[e]), 'r' )
            background.paste(img, (0, 0), img)
    for s in espositions:
        if shadows.has_key(s):
            img=Image.open( os.path.join(BACKGROUND_DIR,shadows[s]), 'r' )
            background.paste(img, (0, 0), img)        


    newW = width

    ratio = float(newW) / w 
    newH = int(ratio * h)
    Nsize = newW, newH

    background.thumbnail(Nsize, Image.ANTIALIAS)
    if save:
        background.save( os.path.join(dir_name, compass_file_name) )
        
    if show:
        background.show()
        
    return (os.path.join(dir_name, compass_file_name), background.size)
