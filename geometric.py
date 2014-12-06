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

import re
from errors import *

def isInstanceLatLng(obj):
    if isinstance(obj, LatLng):
        return True
        
# Classe gestione punto geografico
class LatLng(object):
    """
    Representation of a geographic coordinate.

    Properties:
    lat  latitude [degrees]   (-90 <= lat <= 90)
    lng  longitude [degrees]  (-180 < lon <= 180)

    Constructor:
    LatLng(lat, lng)
    """
    
    # numero di decimali
    decimal = 16
    
    def __init__(self, *args, **kwargs):
    
        # TEST OK
        #
        # args puo' essere una stringa del tipo "-45.9876,179.12345" (lat, lng)
        # args deve avere una coppia di valori numerici (lat e lng) 
        # kwargs deve avere 'lat' e 'lng' come chiavi oppure niente
        # lat compreso tra -90 e +90
        # lng compreso tra -180 e +180
        # lat e lng devono essere numeri float
        #
        # examples:
        # LatLng("-45.9876, 179.12345")
        # LatLng(-45.9876, 179.12345)
        # LatLng(lat = -45.9876, lng = 179.12345)
        #
        
        self._defaultLat = 0.0
        self._defaultLng = 0.0
        
        self._lat, self._lng = self._defaultLat, self._defaultLng
        
        if not self._isPositionValue(*args, **kwargs):
            raise InvalidCoordinateType()
    
    # ogni argomento in value diventa una lista di valori float
    # una lista vuota se non trova valori
    def _match_re(self, *value):
        # trasforma tutto in stringa se diverso tipo
        if type(value) != type('') or type(value) != type(u''):
            value = unicode(value)
        p=re.compile(r"[-+]?\d*\.\d+|\d+", re.IGNORECASE)
        return [float(x) for x in p.findall(value)][:2]
        
    # controlla i valori inseriti se sono compatibili
    # e setta i nuovi valori nelle variabili _lat e _lng
    # se args e kwargs sono nulli, resetta i valori predefiniti
    def _isPositionValue(self, *args, **kwargs):
        # filtra i valori nulli non utilizzabili nella lista args
        args = filter(None, args) 
        
        # Nessuna valore passato
        if len(kwargs.keys()) == 0 and len(args) == 0:
            return True
        
        # Verifica che args sia di uno o due valori
        if len(args) == 1 : 
            # Controllo che il valore passato sia un oggetto LatLng
            if isInstanceLatLng(args[0]): 
                args = args[0].pos
                
            # dovrebbe essere una stringa del tipo '-xxx.dddddddd,-xxx.dddddddd'
            
            # vecchio controllo
            #s = args[0]
            #if type(s) is not type('') and type(s) is not type(u''):
            #    raise StringTypeError(type(s))
            #args = s.split(",")
            
            # ora utilizziamo le regular expressions 
            args = self._match_re(args)
            if len(args) == 2:
                for n in range(len(args)):
                    try:
                        args[n] = float(args[n]) # errore se il valore non e' convertibile in float
                    except ValueError:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        raise FloatError(exc_value)
            else:
                raise IncompatibleCoordinateType()

        elif len(args) == 2:
            args = self._match_re(args)
            
        else:
            raise LenArgsError( len(args) )
        
        # verifica kwargs che sia di due chiavi 'lat' e 'lng'
        kwargs = dict( ( k.lower(), v ) for k,v in kwargs.iteritems() ) #setta le chiavi a lowercase
        if len(kwargs.keys()) == 2:
            if 'lat' not in kwargs.keys() and 'lng' not in kwargs.keys():
                raise KwargsError()
            else:
                lat = kwargs['lat']
                lng =  kwargs['lng']
                LatLng = self._match_re(lat, lng)
                if LatLng == 2:
                    args = [ LatLng[0], LatLng[1] ]
                else:
                    raise IncompatibleCoordinateType()

        # ulteriore controllo sul tipo di valore
        # errore se i valori non sono convertibili in float
        #args = [ float(args[0]) , float(args[1]) ]
        try:
            args = [ float(args[0]) , float(args[1]) ]
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise FloatError(exc_value)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise LatLngError(exc_value)
        
        # controlli sul range di Lat e Lng
        # verifica il range della latitudine
        if not -90 <= args[0] <= 90:
            raise OutOfRangeLatError()
        
        # verifica il range della longitudine
        if not -180 <= args[1] <= +180:
            raise OutOfRangeLngError()
        
        # finalmente
        # imposta i valori _lat e _lng della classe
        self._lat = args[0]
        self._lng = args[1]
        return True 
        
    # converte un valore stringa in oggetto LatLng e ritorna l'istanza
    def setFromString(self, s):
        if type(s) != type('') and type(s) != type(u''):
                raise StringTypeError( type(s) )
        if not self._isPositionValue( s ):
            raise InvalidCoordinateType()
        return self
        
    # Controlla se il punto e' all'interno di un bound geografico(area quadrata)
    # ritorna il punto se il test e' positivo
    # ritorna False altrmenti
    def isBounded(self, NE, SW):
        # NW, SW sono oggetti LatLng
        if not isinstance(NE, LatLng):
            raise NELatLngObjectError()
        if not isinstance(NE, LatLng):
            raise SWLatLngObjectError()
            
        # divide in Lat (N-S) e Lng (W-E)
        LatN = NE.lat
        LatS = SW.lat
        LngE = NE.lng
        LngW = SW.lng
        
        Plat, Plng = self.lat, self.lng 
        # controlla se il punto rientra nell'area geografica
        if (LatS <= Plat <= LatN) and (LngW <= Plng <= LngE):
            return self
        return False
        
    @property
    def lat(self):
        return  self._lat
    
    @lat.setter
    def lat(self, v):
        v = float(v)
        self.setPos(v, self._lng)
        
    @property
    def lng(self):
        return self._lng
        
    @lng.setter
    def lng(self, v):
        v = float(v)
        self.setPos(self._lat, v)
    
    @property
    def pos(self):
        return self._lat, self._lng
    
    # ritorna l'istanza dopo aver settato i nuovi valori
    def setPos(self, *args, **kwargs):
        # args accetta una coppia di valori lat, lng numerici
        # oppure una stringa del tipo "10.00,11.00"
        # kwargs accetta un dizionario {'lat': xxx , 'lng': xxx}
        if not self._isPositionValue( *args, **kwargs ):
            raise InvalidCoordinateType()
        return self
            
    def __len__(self):
        lenght = self.decimal * 2 + 11
        return lenght
    
    # converte in una stringa per la compatibilita' del tipo database
    def to_string(self):
        stringFormat = "{:+0"+str(self.decimal+5)+"."+str(self.decimal)+"f},{:+0"+str(self.decimal+5)+"."+str(self.decimal)+"f}"
        return stringFormat.format(self._lat, self._lng)
        
    def __str__(self):
        return self.to_string()
        
    def __unicode__(self):
        return u"%s"%(self.to_string())
