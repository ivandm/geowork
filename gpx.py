# #################################
# 
# Modulo per la getione dei dati
# gpx e kml
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
#
# #################################

import gpxpy
from contrib.graphElevation import Graphic, Graph_Max_min_points
from contrib import errors

import json, os, xml.dom.minidom
import sys, traceback, copy

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
        
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

EMPTY = (None, False, '', u'')

def isInstanceLatLng(obj):
    if isinstance(obj, LatLng):
        return True
        
        
class Kml(object):
    kml = u"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>%(document_name)s</name>
        <description>%(document_description)s</description>
        <Style id="lineStyle">
            <LineStyle>
                <color>%(color_line)s</color>
                <width>%(width_line)s</width>
            </LineStyle>
        </Style>
        <Placemark>
            <name>%(name_placemark)s</name>
            <styleUrl>%(styleurl_placemark)s</styleUrl>
            <LineString>
                            <altitudeMode>clampToGround</altitudeMode>
                            <extrude>1</extrude>
                <tessellate>1</tessellate>
                <coordinates>
                                %(points)s
                </coordinates>
            </LineString>
        </Placemark>
    </Document>
    </kml>
    """
    attr = {'document_name': u'Adventure2Italy.kml',
            'document_description': u"Adventure2Italy's path.",
            'color_line': u'99ffac59',
            'width_line': u'6',
            'name_placemark': u'Path',
            'styleurl_placemark': u'#lineStyle',
            'points': u''
            }
    
    def setAttr(self, name, value):
        self.attr.update({name, value})
        
    def setCoordintates(self, coordinates):
        # coordinates e' un oggetto stringa del tipo
        # lat,lng,ele lat,lng,ele ... ...
        self.attr.update({'points': coordinates})
        
    def getKml(self):
        return  self.kml % self.attr
        
# Classe gestione dati gpx e kml
class Gpx(object):
    """
        Representation of gpx and kml object.
        staticmethod:
            isGpxFile
            readGpxFile
            gpx2xml
        """
    _systemType = 'm'
    _graphic = None     # cache dell'oggetto grafico
    def __init__(self, gpx_file, *args, **kwargs):
        # qui gpx_file e' una stringa file_path 
        #f = open(gpx_file)
        #data = f.read()
        #f.close()
        
        # qui gpx_file e' una stringa xml
        self.gpx_file = data = gpx_file
        
        # legge il sistema di misura che deve essere 'm' o 'f'
        systemType = kwargs.get('systemType', 'm')
        self.systemType = systemType
    
    # funzione Magic. se non esiste il grafico lo crea alla prima chiamata
    @property
    def graph(self):
        if not self._graphic: #se non esiste genera il grafico
            dom = xml.dom.minidom.parseString(self.gpx_file)     # data is string
            self._graphic = Graphic(dom = dom, systemType = self._systemType)
        return self._graphic # ritorna il grafico della cache
        
        #self.graph.handleTrackFile(dom) #inizializza tutte le variabili della classe Graphic
    def _get_systemType(self):
        return self._systemType
        
    def _set_SystemType(self, system):
        if not system.lower() in ('m', 'f'):
            system = 'm'
        if system.lower() != self._systemType:
            self._graphic = None # elimina il vecchio grafico con il vecchio sistema di misura
            self._systemType = system
    systemType = property(_get_systemType, _set_SystemType, None, "I'm the metric system property.")
    
    @staticmethod
    def isGpxFile(gpx_file):
        # gpx_file is xml (string) or file object
        # ritora True/False
        try:
            doc = gpxpy.parse(gpx_file)
            return True
        except :
            return False 
    
    @staticmethod
    def readGpxFile(gpx_file):
        # gpx_file is xml (string) or file object
        # ritorna un oggetto gpxdata 
        return gpxpy.parse(gpx_file)
     
    @staticmethod
    def gpx2xml(gpx_file):
        # gpx_file is xml (string) or file object
        doc = gpxpy.parse(gpx_file)
        return doc.to_xml()

    @staticmethod
    def getListCoordinates(gpx_file):
        # gpx_file is xml (string) or file object
        # ritorna una lista:
        # [ [latitude, longitude, elevation],
        #   [latitude, longitude, elevation],
        #   ...
        # ]
        doc = gpxpy.parse(gpx_file)
        points = []
        for y in doc.walk():
            x =  y[0]
            points.append([x.latitude, x.longitude, x.elevation])
        return points
        
    @staticmethod    
    def getJsonCoordinates(gpx_file):
        # gpx_file is xml (string) or file object
        # ritorna un oggetto json accessibile
        # da javascript nella i-esima posizione come:
        # 'coordinates.points[i].p.lat'
        # 'coordinates.points[i].p.lng'
        # 'coordinates.points[i].p.ele'
        #
        doc = gpxpy.parse(gpx_file)
        points = []
        for p in doc.walk():
            p = p[0]
            points.append({'p': {'lat': p.latitude,
                                'lng': p.longitude,
                                'ele': p.elevation}
                          })
        d = {
            'points': points
        }
        return json.dumps(d)

    @staticmethod
    def gpx2kml(gpx_file):
        # gpx_file is xml (string) or file object
        # ritorna un oggetto stringa (kml)
        doc = gpxpy.parse(gpx_file)
        points = []
        for y in doc.walk():
            x =  y[0]
            points.append(u"%s %s %s" % (x.latitude, x.longitude, x.elevation))
        #points = u" ".join(points)
        kml = Kml()
        kml.setCoordintates(points)
        return kml.getKml()
    
    def getCoordinatesKml(self, **kwargs):
        # gpx_file is xml (string) or file object
        # ritorna un oggetto lista (("lat,lng"), ("lat,lng"), ... ...)
        doc = gpxpy.parse(self.gpx_file)
        points = []
        lista = doc.walk()
        for y in lista:
            x =  y[0]
            # google KML inverte le coordinate in Lon,Lat
            points.append(u"%s,%s" % (x.longitude, x.latitude))
        return points
    
    
    def getSerieCSV(self,**kwargs):
        # trasforma in csv
        system        = kwargs.get('system', 'm')
        
        # parsing di gpx_file
        # qui gpx_file e' una stringa xml
        data = self.gpx_file
        
        dom = xml.dom.minidom.parseString(data)
        
        self.graph = Graphic()
        graph = self.graph.handleTrackFile(dom)
        
        serie = ["Tempo","Altitude","Ascesa","Discesa"]
        assex = "Distance"
        points = []
                
        for d,a,t,asc,dis in self.graph.serie:
            points.append("%4.1f,%4.1f,%d,%d,%d" % (d*100,t.seconds,a,asc,dis) )
        csv = '\n'.join(points)
        d = {
            'csv': csv,
            'serie': serie,
            'assex': assex,
        }
        return d
        
    def getJsonCSV(self, **kwargs):
        
        system        = kwargs.get('system', 'm')
        # 'basex' il nome della serie di base (vedi graphElevation.Graphic.series)
        basex         = kwargs.get('basex', 'dist') 
        
        # parsing di gpx_file se non ancora fatto
        # qui gpx_file e' una stringa xml
        if not self.graph:
            data = self.gpx_file
            dom = xml.dom.minidom.parseString(data)
            self.graph = Graphic(dom=dom, systemType = system)
            #graph = self.graph.handleTrackFile(dom)
        
        # recupera le serie
        series = self.graph.series()
        if basex == 'dist':
            serie_X = series['dist']; del series['dist']
            serie_Y = series['ele']; del series['ele']
        
        serie_i = zip(serie_X, [serie_Y, series.values()])
        csv = {
               #'serie_XY': '\n'.join(["%f,%f"%(x[0],x[1]) for x in zip(serie_X, serie_Y)]), 
               'serie_XY': zip(serie_X, serie_Y), 
               }
        valori =  {}
        for x, y in zip(serie_X,zip(serie_Y,series['time'],series['lat'],series['lon'],)):
            valori[x] = {'ele': y[0], 
                         'time': y[1],
                         'lat': y[2],
                         'lon': y[3],
                         }
        csv['valori'] = valori;
        # recupera x,y per il grafico
        if system == 'm':
            x = self.graph.distances_meters
            y = self.graph.eles_meters
            pointMaxEle = max( self.graph.eles_meters)
            pointMinEle = min(self.graph.eles_meters)
            
        if system == 'f':    
            x = self.graph.distances
            y = self.graph.eles
            pointMaxEle = max( self.graph.eles)
            pointMinEle = min(self.graph.eles)
        
        points = ["Distance,Altitude"]
        
        pointMax = {'x':'0', 'y': "%4.1f" % pointMaxEle, 'system': system}
        pointMin = {'x':'0', 'y': "%4.1f" % pointMinEle, 'system': system}
        
        for z in zip(x,y):
            if "%4.1f" % z[1] == pointMax['y']: pointMax['x'] = "%4.3f" % z[0]
            if "%4.1f" % z[1] == pointMin['y']: pointMin['x'] = "%4.3f" % z[0]
            points.append("%4.3f,%4.1f" % (z[0],z[1]) )
        #csv['serie_XY'] = '\n'.join(points)
        
        
        d = {
            'csv': csv,
            'serie': 'Altitude',
            'pointMax': pointMax,
            'pointMin': pointMin,
        }
        return d #json.dumps(d)
    
    def _getGraphElevationProfile(self, **kwargs):
        # gpx_file is a file path (string) NECESSARIO
        # name is a file name (string)
        # dir_name is dir path (string)
        
        name        = kwargs.get('name', None)          # 
        dir_name    = kwargs.get('dir_name', None)      # 
        system      = kwargs.get('system', 'm')
        facecolor   = "#%s" % kwargs.get('facecolor', 'ffffff')
        color       = "#%s" % kwargs.get('color', '088A85')
        dpi         = kwargs.get('dpi', 150)
        force_make  = kwargs.get('force_make', False)
        
        # genera il nome del grafico file .png del profilo del file .gpx
        #if system == 'm':
        #    fname_basename = name+'_graphM.png'
        #if system == 'f':
        #    fname_basename = name+'_graphF.png'
                    
        #fname = os.path.join(dir_name, fname_basename)        
        #if os.path.isfile(fname) and not force_make:
        #    return fname_basename    # il file esiste viene restituito il path assoluto
                
        # qui gpx_file e' una stringa file_path 
        #f = open(self.gpx_file)
        #data = f.read()
        #f.close()
        
        # qui gpx_file e' una stringa xml
        data = self.gpx_file
        
        dom = xml.dom.minidom.parseString(data)
        
        self.graph = Graphic()
        graph = self.graph.handleTrackFile(dom)
        
        # ######################
        # ### START PLOTTING ###
        
        w = 10
        h = 4
        fig = Figure(figsize=(w,h), dpi=dpi, facecolor=facecolor)
        
        ax = fig.add_subplot(111, axisbg=facecolor)
        if system == 'm':
            x = self.graph.distances_meters
            y = self.graph.eles_meters
            ax.set_xlabel("Kilometers")
            ax.set_ylabel("Meters")
            
            title = 'Tot ASC/DISC: %0.f/%0.f - Quota Max: %0.1f / Min: %.1f (meters)' % (
                        self.totalAscentDiscent('m')[0] , 
                        self.totalAscentDiscent('m')[1],
                        min(y),  max(y)) 
            ax.set_title(title)
            
        if system == 'f':    
            x = self.graph.distances
            y = self.graph.eles
            ax.set_xlabel("Milies")
            ax.set_ylabel("Feet")
            title = 'Tot ASC/DISC: %0.f/%0.f - Quota Max: %0.1f / Min: %.1f (feet)' % (
                        self.totalAscentDiscent('f')[0] , 
                        self.totalAscentDiscent('f')[1],
                        min(y),  max(y))
            ax.set_title(title)
            
        ax.axis([min(x), max(x), min(y), max(y)])
        ax.fill_between(x, y, color=color)

        # nella view ritornare con il seguente codice
        # response = HttpResponse(content_type='image/png')
        # canvas.print_png(response, dpi=xxx, bbox_inches='tight')
        return FigureCanvas(fig)
    
    def graphProfile_asHttpImagePng(self, **kwargs):

        response    = kwargs.get('response', HttpResponse(content_type='image/png') )
        canvas      = self._getGraphElevationProfile(**kwargs)
        dpi         = kwargs.get('dpi', 150)
        canvas.print_png(response, dpi=dpi, bbox_inches='tight')
    
    def graphPropile_asFigureCanvas(self,**kwargs):        
        figureCanvas = self._getGraphElevationProfile(**kwargs)
        return figureCanvas
               
    def graphAltMaxMin_asHttpImagePng(self, **kwargs):

        response    = kwargs.get('response', HttpResponse(content_type='image/png') )
        Max = "%.0f" % self.graphHighestPoint(kwargs.get('system', 'm'))
        Min = "%.0f" % self.graphLowestPoint(kwargs.get('system', 'm'))
        
        canvas = Graph_Max_min_points(Max = Max, Min = Min, **kwargs)
        dpi    = kwargs.get('dpi', 150)
        canvas.print_png(response, dpi=dpi, bbox_inches='tight')
    
    def graphAltMaxMin_asFigureCanvas(self, **kwargs):
        ##print "#STEP getMaxMinGraphPoints", system
        Max = "%.0f" % self.graphHighestPoint(kwargs.get('system', 'm'))
        Min = "%.0f" % self.graphLowestPoint(kwargs.get('system', 'm'))
        figureCanvas = Graph_Max_min_points(Max = Max, Min = Min, **kwargs)
        return figureCanvas
    def getHighestPoint(self):
        return self.graphHighestPoint()
    def graphHighestPoint(self, systemType = None):
        # systemType: 'm' metri; 'f' feet
        systemType = systemType or self.systemType
        if self.graph:
            return self.graph.getMaxMinEle(systemType)[0]
        else: return -1.0
    def getLowestPoint(self):
        return self.graphLowestPoint()
    def graphLowestPoint(self, systemType = None):
        # systemType: 'm' metri; 'f' feet
        systemType = systemType or self.systemType
        if self.graph:
            return self.graph.getMaxMinEle(systemType)[1]
        else: return -1.0
    def graphMaxMinPoint(self, systemType = 'm'):
        # systemType: 'm' metri; 'f' feet
        if self.graph:
            return self.graph.getMaxMinEle(systemType)
        else: return -1.0,-1.0
    def totalAscent(self, systemType = None):
        # systemType: 'm' metri; 'f' feet
        systemType = systemType or self.systemType
        if self.graph:
            return self.graph.getTotAscentDiscent(systemType)[0]
        else: return -1.0
    def totalDiscent(self, systemType = None):
        # systemType: 'm' metri; 'f' feet
        systemType = systemType or self.systemType
        if self.graph:
            return self.graph.getTotAscentDiscent(systemType)[1]
        else: return -1.0
    def totalAscentDiscent(self, systemType = 'm'):
        # systemType: 'm' metri; 'f' feet
        if self.graph:
            return self.graph.getTotAscentDiscent(systemType)
        else: return -1.0,-1.0
    def totalDistance(self, systemType = None):
        # systemType: 'm' metri; 'f' feet
        systemType = systemType or self.systemType
        if self.graph:
            return self.graph.getTotDistance(systemType)
        else: return -1.0
    def totalTime(self):
        if self.graph:
            return self.graph.moving_time
        else: return -1.0
    def totalTimeStr(self):
        t = self.totalTime()
        d = t.seconds/86400
        h = t.seconds/3600
        m = t.seconds%3600/60
        if d > 0: df = "%dd:" % d
        else: df = ''
        return df+"%dh:%dm" % (h, m)
        
    def getTotalClimb(self, systemType = 'm'):
        # systemType: 'm' metri; 'f' feet
        if self.graph:
            return self.graph.getTotalClimb(systemType)
        else: return -1.0
    def getSystem(self):
        if self.systemType == 'm': 
            distance = 'km'
        else:
            distance = 'mi'
        return {'elevation': self.systemType, 'distance': distance}
        
class ManagerGpx(Gpx):
    
    FieldFile = None
    
    def __init__(self, gpx_file = None, *args, **kwargs):
        super(ManagerGpx, self).__init__(gpx_file, *args, **kwargs)
    