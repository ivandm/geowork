# -*- coding: ISO-8859-1 -*-

#################
# FORMS FORM    #
#    and        #
# FORMS FIELDS  #
#################
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

# A class that is responsible for:
# doing VALIDATION, e.g. an EmailField that makes sure its data is a valid email address.
# choce a WIDGET geoWidget's type
# 

"""
Field forms classes.
"""

from django import forms
from django.core import validators
from django.core.validators import EMPTY_VALUES
from django.utils.encoding import smart_text, force_text
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import sys, traceback

#################
# FORMS FIELDS  #
#    SECTION    #
#################

from geowork.forms import geoWidgets
from geowork.geometric import LatLng
from geowork.gpx import Gpx
from geowork.compass import COMPASS_espositions_CHOICE, Compass
from geowork import compass
from geowork.imageComposer import ImageComposerManager

from gpxdata import Document

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

list_files_image = {
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

DEFAULTS_SEASON_ATTR = {    
    'DEST_PATH'         : "best_year_files",
    'list_files_image'  : list_files_image,
    'BG_IMG'            : "year_bg.png",
    'BG_DIR'            : "geowork/images",
    'EXT_NAME'          : "_year.png"
    }
    
class SeasonField(forms.ChoiceField):
    widget = geoWidgets.SeasonField
    
    def __init__(self, choices=(), *args, **kwargs):
        
        self.custom_attrs = {}
        custom_key_kwargs = ['list_files_image', 'DEST_PATH', 'BG_IMG', 
                             'BG_DIR', 'EXT_NAME']
        for k in custom_key_kwargs:
            self.custom_attrs[k] = kwargs.get(k, DEFAULTS_SEASON_ATTR[k])
            if kwargs.has_key(k): del kwargs[k]
                
        super(SeasonField, self).__init__(choices=MONTHS_SELECT_LIST_CHOICE, *args, **kwargs)
    
    def to_python(self, value):
        "Returns a list of Unicodes object."
        # sostituito da ImageComposerManager
        
        #lista = super(SeasonField, self).to_python(value)
        return_value = None
        if isinstance(value, ImageComposerManager):
            return_value = value
        elif value and type(value) in (list, tuple):
            return_value = ImageComposerManager(composerList=value, **self.custom_attrs)
        elif value and type(value) in (str, unicode):
            return_value = ImageComposerManager(composerList=','.split(value), **self.custom_attrs)
        else:
            return_value = ImageComposerManager(composerList=[], **self.custom_attrs)
        return return_value
        
    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        
        if isinstance(value, ImageComposerManager):
            value = value.composerList
        if value and type(value) in (list,tuple):
            for v in value:
                super(SeasonField, self).validate(v)
                if v and not self.valid_value(v):
                    raise ValidationError(self.error_messages['invalid_choice'] % {'v': v})
        else:
            super(SeasonField, self).validate(value)
            if value and not self.valid_value(value):
                raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})
                    
            
class CompassField(forms.ChoiceField):
    widget = geoWidgets.CompassWidget

    # TEST OK
    
    # choices e' dato di default
    # essendo questa classe specializzata
    def __init__(self, choices=(), *args, **kwargs):
        self.path_compass = None
        super(CompassField, self).__init__(choices=COMPASS_espositions_CHOICE, *args, **kwargs)
        
    def to_python(self, value):
        "Returns a list of Unicodes object."
        
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
        
    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        if isinstance(value, Compass):
            value = value.esposition
        if type(value) in (list,tuple):
            for v in value:
                super(CompassField, self).validate(v)
                if v and not self.valid_value(v):
                    raise ValidationError(self.error_messages['invalid_choice'] % {'v': v})
        else:
            super(CompassField, self).validate(value)
            if value and not self.valid_value(value):
                raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})
            
            
# Campo gestione del file gpx
class GpxField(forms.FileField):
    widget = geoWidgets.GpxFieldWidget
    
    def validate(self, value):
        # legge il contenuto del file come unicode
        if value:
            file = value.file            
            if not Gpx.isGpxFile(file):
                error_prefix = u"File: '%s' %s. " % (value.name, type(file))
                error_suffix = u"%s" % _(u"Il File non sembra essere del tipo gpx.")
                error = error_prefix + error_suffix
                raise ValidationError(_(error))
            else:
                pass
        return super(GpxField, self).validate(value)
        
class LatLngField(forms.CharField):
    widget = geoWidgets.LatLngTextInputWidget
    
        
    # max_length deve essere la lunghezza massima della stringa geometric.LatLng.to_string()
    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        # decimali di default per le coordinate 
        # setta max_length come lunghezza della stringa delle coordinate
        # dall'oggetto LatLng
        # max_length = len( LatLng() )
        p = LatLng()
        self.max_length = len(p)
               
        super(LatLngField, self).__init__(*args, **kwargs)
    
    def validate(self, value):
        "Check if value consists only of valid geografic coordinates."
        try:
            LatLng(value)
            
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise ValidationError(exc_value)
        
        # Use the parent's handling of required fields, etc.
        super(LatLngField, self).validate(value)

#################
#   FORMS FORM  #
#    SECTION    #
#################

from django import forms

COMPASS_CHOICES = COMPASS_espositions_CHOICE

# per il TEST
class CompassForm(forms.Form):
    compass = CompassField()
    
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = GpxField( )