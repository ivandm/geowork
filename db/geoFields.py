# -*- coding: ISO-8859-1 -*-

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

from django.db import models
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import default_storage


from geowork.geometric import LatLng
from geowork.compass import createCompass, Compass
from geowork import compass, gpx
from geowork.forms import geoFields
from geowork.imageComposer import ImageComposerManager
from geowork import imageComposer

# gestisce oggetto che 'Crea il calendario stagione'
class SeasonField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "Best months of the year"
    #
    # TEST OK
    #  
    def __init__(self, *args, **kwargs):
        
        self.custom_attrs = {}
        custom_key_kwargs = ['list_files_image', 'DEST_PATH', 'BG_IMG', 
                             'BG_DIR', 'EXT_NAME']
        for k in custom_key_kwargs:
            if kwargs.has_key(k): 
                self.custom_attrs[k] = kwargs[k]
                del kwargs[k]
        
        # in django ver 1.7 da errore in 'manage.py migrate'  self.custom_attrs['list_files_image'].keys()
        default = {}
        if self.custom_attrs.has_key('list_files_image'):
            self.max_length = len( ','.join( self.custom_attrs['list_files_image'].keys() ))
            default = {'max_length': self.max_length}
        
        kwargs.update(default)
        super(SeasonField, self).__init__(*args, **kwargs)
        
    def contribute_to_class(self, cls, name):
        super(SeasonField, self).contribute_to_class(cls, name)
        
    def get_internal_type(self):
        return "CharField"
        
    def to_python(self, value):
        # ritorna sempre una istanza ImageComposerManager
        return_value = None
        if isinstance(value, ImageComposerManager):
            return_value = value
        elif value and type(value) in (list, tuple):
            return_value = ImageComposerManager(composerList=value, **self.custom_attrs)
        elif value and type(value) in (str, unicode):
            return_value = ImageComposerManager(composerList=value.split(','), **self.custom_attrs)
        else:
            return_value = ImageComposerManager(composerList=[], **self.custom_attrs)
        return return_value
        
    def get_prep_value(self, value):
        # ritorna sempre un valore stringa per il DB
        if value and type(value) in (unicode, str):
            return value
        if isinstance(value, ImageComposerManager):
            return u','.join(value.composerList)
        if type(value) in (list, tuple):
            return u','.join(value)
        return ""
        
    def formfield(self, **formfield):
        
        # Returns the default form field to use when this field is displayed in a model. 
        # This method is called by the ModelForm helper.
        formfield.update(self.custom_attrs)
        form = super(SeasonField, self).formfield(form_class=geoFields.SeasonField, **formfield)
        form.custom_attrs = self.custom_attrs
        return form
        
# gestisce la l'oggetto createCompass
# il path del file generato
class CompassField(models.Field):
    __metaclass__ = models.SubfieldBase
    #
    # TEST OK
    #  
    description = "Compass image espositions field"
    
    def __init__(self, *args, **kwargs):
        
        # setta il path per le immagini compass
        self.path_compass = ""
        if kwargs.has_key('path_compass'):
            self.path_compass = kwargs['path_compass']
            del kwargs['path_compass'] # lo elimina per la classe parent           
        
        # setta in automatico max_length come lunghezza del campo nel db
        self.max_length = compass.lenField()
        default = {'max_length': self.max_length}
        
        kwargs.update(default)
        super(CompassField, self).__init__(*args, **kwargs)
    
    def get_internal_type(self):
        return "CharField"
        
    def to_python(self, value):
        # ritorna sempre una lista
        
        return_value = None
        if isinstance(value, Compass):
            return_value = value
        elif value and type(value) in (list, tuple):
            return_value = Compass(value, self.path_compass)
        elif value and type(value) in (str, unicode):
            return_value = Compass(value.split(','), self.path_compass)
        else:
            return_value = Compass([], self.path_compass)
        return return_value
    
    def get_prep_value(self, value):
        if value and type(value) in (unicode, str):
            return value
        if isinstance(value, Compass):
            return u"%s"%u','.join(value.esposition)
        return '' #u"%s"%u','.join(value)
        
        
    def contribute_to_class(self, cls, name):
        super(CompassField, self).contribute_to_class(cls, name)
            
    # implementare il campo form da utilizzare per il template
    def formfield(self, **kwargs):
        
        # Returns the default form field to use when this field is displayed in a model. 
        # This method is called by the ModelForm helper.
        
        form = super(CompassField, self).formfield(form_class=geoFields.CompassField, **kwargs)
        form.path_compass = self.path_compass
        return form
        

from django.core.files.storage import FileSystemStorage, Storage

class GpxFieldFile(models.fields.files.FieldFile):
    _cache_gpx = None
     
    @property
    def gpx(self):
        if self._cache_gpx: return  self._cache_gpx
        self.open()
        data = self.file.read()
        self.close()
        self._cache_gpx = gpx.ManagerGpx(data)
        return self._cache_gpx
# Campo di gestione del file gpx
class GpxField(models.FileField):
    # TEST OK
    attr_class = GpxFieldFile
    #description = "Gpx file field"
   
    def __init__(self, *args, **kwargs):
        #kwargs.update({'storage': GpxStorage()})
        super(GpxField, self).__init__(*args, **kwargs)
    
    # #################################################
    # TODO: modificare qui i due metodi con il nuovo oggetto
    #       ManagerGpx ?? forse!!
    # implementare il campo form da utilizzare per il template
        
    def contribute_to_class(self, cls, name):
        super(GpxField, self).contribute_to_class(cls, name)
                    
    def formfield(self, **kwargs):
        # Returns the default form field to use when this field is displayed in a model. 
        # This method is called by the ModelForm helper.
        
        # Utilizza GpxField di geoFields. Campi forms personalizzati 
        defaults = {'form_class': geoFields.GpxField}
        kwargs.update(defaults)
        return super(GpxField, self).formfield(**kwargs)
        
# Campo django di gestione dei punti geografici
# i punti geografici sono oggetti istanza LatLng
class LatLngField(models.CharField):

    # TEST OK
    
    description = "Latitude and Longitude field"

    # If you’re handling custom Python types. 
    # You must use special metaclass "models.SubfieldBase"
    # This ensures that the to_python() method, documented below, 
    # will always be called when the attribute is initialized.
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        
        # decimali di default per le coordinate 
        # setta max_length come lunghezza della stringa delle coordinate
        # dall'oggetto LatLng
        # max_length = len( LatLng() )
        p = LatLng()
        self.max_length = len(p)
        default = {'max_length': self.max_length}
        kwargs.update(default)
               
        super(LatLngField, self).__init__(*args, **kwargs)
        
    def db_type(self, connection):
        # calcola la lunghezza del campo char del database
        p = LatLng()
        lenght = len(p) #self.max_length * 2 + 11
        return 'char(%s)'%lenght # type this: "-041.90997180,-012.53650420"
        
    # Converting database values to Python objects
    # quindi da stringa ad oggetto LatLng
    def to_python(self, value):
        if isinstance(value, LatLng):
            return value

        # se non e' un oggetto LatLng istanzia il nuovo oggetto LatLng
        p = LatLng()
        p.setPos(value)
        return p
    
    # Converting Python objects to query values
    # quindi da oggetto LatLng a stringa (??)
    def get_prep_value(self, value):
        if isinstance(value, LatLng):
            return value.to_string()
        
        # se non e' un oggetto LatLng tenta la conversione
        # e ritorna la stringa
        p = LatLng()
        p.setPos(value)
        return p.to_string()
        
    # implementare la ricerca nel db sul campo
    # per ricercare se la coordinata e' all'interno di un'area (bound)
    # ma forse debbo spostare la ricerca nel Manager con un metodo specifico
    # che controlla tutti i campi, e ritorna una lista iterabile (con yeld)
    # per avere le istanze di modello per i normali metodi di ricerca
    # esempio:
    # mymodel.object.bounded(NE, SW).filter(...)
    
    def get_prep_lookup(self, lookup_type, value):
        value = self.get_prep_value(value)
        return super(LatLngField, self).get_prep_lookup(lookup_type, value)
        
    # implementare il campo form da utilizzare per il template
    def formfield(self, **kwargs):
        # Returns the default form field to use when this field is displayed in a model. 
        # This method is called by the ModelForm helper.
        
        # Utilizza LatLngField di geoFields. Campi forms personalizzati 
        defaults = {'form_class': geoFields.LatLngField}
        kwargs.update(defaults)
        return super(LatLngField, self).formfield(**kwargs)

    def get_internal_type(self):
        return 'GeoPosition field'