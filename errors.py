# -*- coding: ISO-8859-1 -*-
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

import sys, traceback
from django.utils.translation import ugettext_lazy as _

def chatchError(): #??
    return 

class GenericError(Exception):
    def __init__(self, value = u"Generic Error"):
        self.value = value
    
    def __str__(self):
        return self.value
     
    def __unicode__(self):
        return self.value

class GpxFileError(GenericError):
    def __init__(self, file = ''):
        super(GpxFileError, self)
        self.value = u"%s"%_(u"'%s' non sembra essere un file GPS (.gpx) compatibile o file corrotto." % str(file) )
        
class LatLngError(Exception):
    def __init__(self, value):
        self.value = value
     
    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value

 
class InvalidCoordinateType(LatLngError):
    def __init__(self):
        super(InvalidCoordinateType, self)
        self.value = u"%s"%_(u"Values are not coordiates type.")
         
class IncompatibleCoordinateType(LatLngError):
    def __init__(self):
        super(IncompatibleCoordinateType, self)
        self.value = u"%s"%_(u"Values aren't coordinate compatible format. String must is '-xxx.dddddddd,-xxx.dddddddd' (lat,lng)")

class StringTypeError(LatLngError):
    def __init__(self, msg):
        super(StringTypeError, self)
        self.value = u"%s"%_(u"Values is type %s. It must be a string object."%msg)

class LenArgsError(LatLngError):
    def __init__(self, msg):
        super(LenArgsError, self)
        self.value = u"%s"%_(u"Values are %s. LatLng wants max 2 values in args."%msg)

class KwargsError(LatLngError):
    def __init__(self):
        super(KwargsError, self)
        self.value = u"%s"%_(u"LatLng want keys 'lat' and 'lng' in kwargs")

class OutOfRangeLatError(LatLngError):
    def __init__(self):
        super(OutOfRangeLatError, self)
        self.value = u"%s"%_(u"Lat is must between -90 and +90 degrees")

class OutOfRangeLngError(LatLngError):
    def __init__(self):
        super(OutOfRangeLngError, self)
        self.value = u"%s"%_(u"Lng is must between -180 and +180 degrees")

class NELatLngObjectError(LatLngError):
    def __init__(self):
        super(OutOfRangeLngError, self)
        self.value = u"%s"%_(u"NE value must an LatLng object instance")

class SWLatLngObjectError(LatLngError):
    def __init__(self):
        super(OutOfRangeLngError, self)
        self.value = u"%s"%_(u"SW value must an LatLng object instance")

class FloatError(LatLngError):
    def __init__(self, value):
        super(FloatError, self)
        self.value = u"%s"%_(u"%s. Coodinate must be type '-xxx.dddddddd'"%value)
