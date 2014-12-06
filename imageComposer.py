###################
# MODELS DATABASE #
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

list_year_files_image = {
    u'JAN': ['year_jan.png'],
    u'FEB': ['year_feb.png'],
    u'MAR': ['year_mar.png'],
    u'APR': ['year_apr.png'],
    u'MAY': ['year_may.png'],
    u'JUN': ['year_jun.png'],
    u'JUL': ['year_jul.png'],
    u'AUG': ['year_aug.png'],
    u'SEP': ['year_sep.png'],
    u'OCT': ['year_oct.png'],
    u'NOV': ['year_nov.png'],
    u'DIC': ['year_dic.png'],
    }
MONTHS_SELECT_LIST_CHOICE = (
        (u'JAN', _(u'Gennaio' )),
        (u'FEB', _(u'Febbraio' )),
        (u'MAR', _(u'Marzo')),
        (u'APR', _(u'Aprile' )),
        (u'MAY', _(u'Maggio')),
        (u'JUN', _(u'Giugno' )),
        (u'JUL', _(u'Luglio' )),
        (u'AUG', _(u'Agosto' )),
        (u'SEP', _(u'Settembre' )),
        (u'OCT', _(u'Ottobre' )),
        (u'NOV', _(u'Novembre' )),
        (u'DIC', _(u'Dicembre' )),
        )
        
class Img(object):

    # BG_IMG = 'year_bg.png'      # il nome dell'imagine background
    # BG_DIR = 'geowork/images'   # la directory dove sono le immagini base da comporre
    # EXT_NAME = '_year.png'      # estensione del file immagine genrato da aggiungere a 'path'         
    
    TEMPLATE_FILE_OUT = "_DB_%s_DB_%s"

    def __init__(self, path, composerList, width, BG_IMG, BG_DIR, EXT_NAME, thumbnail, list_files_image):
        self.BG_IMG             = BG_IMG
        self.BG_DIR             = BG_DIR
        self.EXT_NAME           = EXT_NAME
        self.composerList       = composerList
        self.width              = width
        self.path               = path
        self.thumbnail          = thumbnail
        self.list_files_image   = list_files_image
        
        out_file_name, background_size = self.createImage()
        
        self.out_file_name = out_file_name
        self.background_size_w = background_size[0]
        self.background_size_h = background_size[1]
    
    @property
    def path_name(self):
        #print self.out_file_name.replace('\\','/')
        return self.out_file_name.replace('\\','/')
    
    @property
    def w(self):
        return self.background_size_w
        
    @property    
    def h(self):
        return self.background_size_h
    
    def createImage(self):
        show, save = False, True
        # path include il nome del file
        # la funzione createCompass aggiunge in automatico
        # l'estenzione _compass.png
        
        # in caso di composerList = [] genera solo l'immagine file background
        composerList    = self.composerList
        dir_name        = self.path
        width           = self.width        
        
        OUT_TEM_NAME = self.TEMPLATE_FILE_OUT % ("-".join(composerList), width)
        out_file_name = OUT_TEM_NAME + self.EXT_NAME
        
        # se il file esiste, non genera nulla
        # ritorna il file e risparmia risorse
        if os.path.isfile(os.path.join(dir_name, out_file_name)):
            im = Image.open( os.path.join(dir_name, out_file_name), 'r' )
            return os.path.join(dir_name, out_file_name), im.size
        
        background=Image.open( os.path.join(self.BG_DIR, self.BG_IMG), 'r' )
        w,h = background.size

        # aggiunge solo le immagini se presenti nei valori predefiniti
        for e in composerList:
            if self.list_files_image.has_key(e):
                for img_file in self.list_files_image[e]:
                    img = Image.open( os.path.join(self.BG_DIR,img_file), 'r' )
                    background.paste(img, (0, 0), img)
                    img.close()

        newW = width

        ratio = float(newW) / w 
        newH = int(ratio * h)
        Nsize = newW, newH

        background.thumbnail(Nsize, Image.ANTIALIAS)
        if save:
            background.save( os.path.join(dir_name, out_file_name) )
            
        if show:
            background.show()
            
        return (os.path.join(dir_name, out_file_name), background.size)
    
class ImageComposerManager(object):
    def __init__(self, 
                DEST_PATH, list_files_image,        #obbligatori
                BG_IMG, BG_DIR, EXT_NAME,           #obbligatori
                
                composerList = [],                  #una lista contenente le chiavi di 'list_files_image'
                
                prefix_name = "prefix_", width=250, #futura implementazione
                thumbnail = 1.0,                    #futura implementazione
                ):
        
        self.composerList = composerList            # list. parametro passato dal DB. Valori contengono le chiavi della lista immagini
        self.path = DEST_PATH                       # string. path delle immagini composte finali
        self.list_files_image = list_files_image    # dict. dizionario lista immagini. le chiavi saranno le stesse del DB
        self.BG_IMG = BG_IMG                        # string. il nome dell'imagine background
        self.BG_DIR = BG_DIR                        # string. la directory dove sono le immagini base da comporre
        self.EXT_NAME = EXT_NAME                    # string. estensione del file immagine genrato da aggiungere a 'path'  
        self.prefix_name = prefix_name              # string. per future implementazioni
        self.width = width                          # int. pixels delle dimensione del file finale generato
        self.thumbnail = thumbnail                  # float. per future implementazioni
        
    
    @property
    def getComposerListStr(self):
        return u",".join(self.composerList)
        
    @property
    def image(self):
        return Img(path=self.path, composerList=self.composerList, width=self.width, thumbnail=self.thumbnail,
                   BG_IMG=self.BG_IMG, BG_DIR=self.BG_DIR, EXT_NAME=self.EXT_NAME, list_files_image=self.list_files_image)
    
    def lenField(self):
        if self.list_files_image:
            l = []
            for k,v in self.list_files_image:
                l.append(k)
            return len(','.join(l))
        return None
        
    def __len__(self): 
        return len(self.composerList)
    
    def __iter__(self):
        return self.composerList.__iter__()
        
    def __str__(self):
        return "%s" % ImageComposerManager.__name__
        
    def __unicode__(self):
        return u"%s" % self.__str__()
