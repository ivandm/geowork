#! /usr/bin/env python

# #################################
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

import sys, os, math, datetime, xml.dom.minidom
from geowork import errors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    import pylab
    have_pylab = True
except ImportError:
    have_pylab = False
    #print "pylab isn't installed; will #print stats only, no plotting"

#import matplotlib.pyplot as plt
#from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

# Climb threshold: any short climb that doesn't gain more than
# this number of feet won't be counted toward total climb.
# GPS units (at least my Vista CX) have a lot of 1-2'
# fluctuations that vastly overestimate the climb total;
# just swinging the bag around, or unhooking it from your belt
# to check your current position, can do that.
CLIMB_THRESHOLD = 4 #feet

# How fast do we have to be moving to count toward the moving average speed?
# This is in miles/hour.
SPEED_THRESHOLD = .5 #miles/hour

METERS2FEET = 3.2808399
FEET2METERS = 0.3048
KM2MI = 0.62137119
MI2KM = 1.609344

def Graph_Max_min_points(Max = 'Max', Min = 'min', **kwargs):
    # Max, Min sono i valori da inserire come etichette nel grafico
    
    system      = kwargs.get('system', 'm')
    facecolor   = "#%s" % kwargs.get('facecolor', 'ffffff')
    color       = "#%s" % kwargs.get('color', '088A85')
    dpi         = kwargs.get('dpi', 150)
    force_make  = kwargs.get('force_make', False)
        
    #print "#START Graphic icon elevation"
    #file_name = file_name + '_max-min-points-%s.png' % system
    
    fig = Figure(figsize=(5,3), dpi=dpi, facecolor=facecolor)
    
    ax = fig.add_subplot(111)
    
    x = [ 0.0, 3.0, 6.0]
    y = [ 0.0, 8.0, 0.0]
    ax.fill_between(x, y, linewidth=2, color=color)

    x = [5, 9.0, 12.0]
    y = [1, 04.0, 00.0]
    ax.fill_between(x, y, linewidth=2, color=color)

    ax.axis([0.0, 20.0, 0.0, 10.0])
    ax.axis('off')

    ax.annotate("%s %s" % (Max, system),
                xy=(3.5, 8), xycoords='data',
                xytext=(20, 8), textcoords='data',
                size=48, va="center", ha="center",
                arrowprops=dict(arrowstyle="-",
                                connectionstyle="arc3,rad=-0.1"), 
                color=color,
                )

    ax.annotate("%s %s" % (Min, system),
                xy=(9.5, 4), xycoords='data',
                xytext=(20, 4), textcoords='data',
                size=48, va="center", ha="center",
                arrowprops=dict(arrowstyle="-",
                                connectionstyle="arc3,rad=0.1"), 
                color=color,
                )
    #plt.savefig(os.path.join(dir_name, file_name) , bbox_inches='tight')
    #plt.close("all")
    #plt.close(fig)
    
    #print " #END Graphic icon elevation"
    ##print "os.path.join(dir_name, file_name)", os.path.join(dir_name, file_name)
    #plt.show()
    return FigureCanvas(fig)
    #return file_name
  
# Graphic NON CREA IL GRAFICO (nome infelice, ma oramai...)
# gestisce solo i dati estrapolati dal file gpx
# per essere usati per la creazione del grafico
class Graphic:

    # tempo e spazio ponderati a seconda il tipo di traccia
    # tracking, hiking : passo d'uomo
    # running: corsa d'uomo in montagna
    # biking: passo ciclabile su strada asfaltata
    # downhill: passo discesa mountainbike
    # canyoning: ??
    # scialpinismo: ??
    # alpinismo: ?? 
    # ferrata: misto tracking e alpinismo
    # 
    VEL_RIF_MIN = 0.5       # velocita' minima km/h
    VEL_RIF_MAX = 10.0      # velocita' massima km/h
    ELE_RIF_MIN = 0.5       # distanza minima tra due punti in metri
    ELE_RIF_MAX = 10.0      # distanza massima tra due punti in metri
    
    def __init__(self, *args, **kwargs):
       
        #Queste variabili servono come serie di dati utili
        #self.dati [ [lat, lon, ele, DELTAdistanza, time_delta] ]
        self.dati = [ ]
        
        # [ {total_dist, ele, total_tempo, total_climb, total_slope}, ... ]
        self.baseSerie = []
        
        self.last_ele = -10000  # inizializzazione
        
        # The variables we're going to plot:
        self.times = [ ]
        self.eles = [ ]
        self.eles_meters = [ ]
        self.distances = [ ]
        self.distances_meters = [ ]

        # Some evil globals because python doesn't have static variables:
        self.lastlat = 0
        self.lastlon = 0
        self.lastele = -1
        self.total_dist = 0
        self.total_climb = 0
        self.total_discent = 0
        self.this_climb = 0
        self.this_climb_start = 0

        self.lasttime = None
        self.moving_time = datetime.timedelta(0)
        self.stopped_time = datetime.timedelta(0)

        # variabili globali (metri)
        self.total_climbing = 0      # salita totale
        self.total_sloping = 0       # discesa totale
        self.total_last_ele = -1     # varibile di partenza
        self.total_min_ele = 0.1     # minima differenza di salita/discesa

        self.global_dist_miglia = 0
        self.global_dist = 0                       # distanza totale in km
        self.global_dist_meter_tollerance = 0.001  # distanza minima in km

        self.global_max_ele = 0      # massima elevazione
        self.global_min_ele = 0      # minima elevazione

        systemType = kwargs.get('systemType', 'm')
        dom        = kwargs.get('dom', None)
        if dom:
            self.handleTrackFile(dom)
            self.makeBaseSerie(systemType)
            
    def getTotalClimb(self, systemType = 'm'):
        if not systemType in ('m','f'):
            return None, None
        if systemType == 'm':
            return self.total_climb * FEET2METERS
        else:
            return self.total_climb
            
    def getVal(self, parent, name) :
        nodeList = parent.getElementsByTagName(name)
        if len(nodeList) < 1 :
            return "No " + name + " element"
        children = nodeList[0].childNodes
        if len(children) < 1 :
            return "No " + name + " children"
        node = children[0]
        if node.nodeType != node.TEXT_NODE:
            return name + " isn't a text node"
        return node.data

    # calcola la massima e minima elevazione
    def _max_min_ele(self, points):
        # tutto in metri
        ele_points = [ float(self.getVal(point, "ele")) for point in points ]
        self.global_max_ele = max(ele_points)
        self.global_min_ele = min(ele_points)
    
    def getMaxMinEle(self, systemType = 'm'):
        # systemType: 'm' metri; 'f' feet
        if not systemType in ('m','f'):
            return None, None
        if systemType == 'm':
            return self.global_max_ele, self.global_min_ele
        else:
            return self.global_max_ele * METERS2FEET, self.global_min_ele * METERS2FEET
    
    def getTotAscentDiscent(self,  systemType = 'm'):
        # systemType: 'm' metri; 'f' feet
        if not systemType in ('m','f'):
            return None, None
        if systemType == 'm':
            return self.total_climbing, self.total_sloping
        else:
            return self.total_climbing * METERS2FEET, self.total_sloping * METERS2FEET
    
    def getTotDistance(self,  systemType = 'm'):
        # systemType: 'm' Km; 'f' Mi
        if not systemType in ('m','f'):
            return None
        if systemType == 'm':
            return self.total_dist * MI2KM
        else:
            return self.total_dist
            
    # calcola il totale dei metri saliti e discesi    
    def accumulate_climb_slope(self, ele):
        #global self.total_climbing, self.total_sloping, self.total_last_ele
        if self.total_last_ele < 0:
            self.total_last_ele = ele
        else:
            this_ele = ele - self.total_last_ele
            self.total_last_ele = ele
            if abs(this_ele) >= self.total_min_ele:
                #self.total_last_ele = ele
                if this_ele > 0 :
                    self.total_climbing = self.total_climbing + this_ele
                if this_ele < 0:
                    self.total_sloping = self.total_sloping + abs(this_ele)
            
    def accumulate_climb(self, ele) :
        if self.lastele >= 0 :             # Not the first call
            if ele > self.lastele :        # Climbed since last step
                if self.this_climb == 0 :
                    self.this_climb_start = self.lastele
                self.this_climb = self.this_climb + ele - self.lastele            
            else :
                if self.this_climb > CLIMB_THRESHOLD :
                    self.total_climb = self.total_climb + self.this_climb
                    self.this_climb = 0
                elif ele <= self.this_climb_start :
                    # We got a little hump but it isn't big enough to count;
                    # probably an artifact like taking the GPS out of its case
                    # or getting off the bike or something. So reset.
                    self.this_climb = 0
        self.lastele = ele

    # parsing dei dati gpx, crea le serie lat, lon, ele, delta_time
    def handleTrackPoint(self, point) :
        #global self.lastlat, self.lastlon, self.lasttime, self.total_dist, self.moving_time, self.stopped_time
        time = datetime.datetime.strptime(self.getVal(point, "time"),
                                          '%Y-%m-%dT%H:%M:%SZ')
        lat = float(point.getAttribute("lat"))
        lon = float(point.getAttribute("lon"))
        ele = float(self.getVal(point, "ele"))
        if self.last_ele < -9000 :
            self.last_ele = ele
        
        # calcola il totale dei metri saliti e discesi    
        self.accumulate_climb_slope(ele)
        self.eles_meters.append(ele)
        
        # calcolo della distanza e delle serie *utili*
        if self.lastlat != 0 and self.lastlon != 0 :
            #VARIABILI: self.global_dist, self.global_dist_miglia, self.dati
            
            dist = math.sqrt((lat - self.lastlat)**2 + (lon - self.lastlon)**2) * 69.046767
                # 69.046767 converts nautical miles (arcminutes) to miles
            self.total_dist += dist
            
            # convere da miglia a km
            self.global_dist_miglia = self.total_dist * 1.609344
            
            delta_t = time - self.lasttime   # This is a datetime.timedelta object
            speed = dist / delta_t.seconds * 60 * 60    # miles/hour
            if speed > SPEED_THRESHOLD :
                self.moving_time += delta_t
                ##print "moving\t",
            else :
                self.stopped_time += delta_t
                ##print "stopped\t",
            
            # lista di dati *utili* per elaborazione grafica
            delta_ele = abs(ele - self.last_ele)            # in metri
            self.last_ele = ele
            delta_dist = dist * 1.609344                    # converte da miglia a km
            delta_time = delta_t                            # datetime.timedelta object
            vel = delta_dist / delta_t.seconds * 60 * 60    # km/hour
           
            # prende il dato filtrato da una velocita' minima e massima
            # quindi tempo e spazio ponderati a seconda il tipo di traccia
            if self.VEL_RIF_MIN <= vel <= self.VEL_RIF_MAX: #or self.ELE_RIF_MAX <= delta_ele <= self.ELE_RIF_MAX:   
                #self.dati = [ [lat, lon, ele, delta_dist, delta_time], ... ]
                self.dati.append( [lat,lon,ele,delta_dist,delta_time] )
            
        ele = round(ele * 3.2808399, 6)      # convert from meters to feet
        self.lasttime = time
        self.accumulate_climb(ele)

        self.lastlat = lat
        self.lastlon = lon

        ##print self.total_dist, ele, "\t", time, lat, lon, "\t", self.total_climb
        ##print self.total_dist, ele, "\t", time, self.total_climb
        ##print self.total_dist, ele, "\t", time, self.total_climb

        self.distances.append(self.total_dist)
        self.distances_meters.append(self.global_dist_miglia)
        
        self.eles.append(ele)
    
    def makeBaseSerie(self, systemType='m'):
        if not systemType in ('m','f'):
            systemType = 'm'
        systemConvElev = 1
        systemConvDist = 1
        
        if systemType == 'f':
            systemConvElev = METERS2FEET
            systemConvDist = KM2MI
        serie = []
        
        #self.dati = [ [lat, lon, ele, delta_dist, delta_time], ... ]
        for lat, lon, ele, delta_dist, delta_time in self.dati:
            serie.append(
                {
                'lat': lat, 
                'lon': lon, 
                'ele': ele * systemConvElev ,
                'delta_dist': delta_dist * systemConvDist, 
                'delta_time': delta_time
                }
            )
        self.baseSerie = serie
        
    def series(self):
        # le conversioni in 'metri' o 'feet' vengono fatte alla creazione delle serie
        
        # Nomi delle serie presenti
        #'lat'      laitudine
        #'lon'      longitudine
        #'ele'      elevazione (metri o feet)
        #'dist'     distanza accumulata (km o mi)       # possibile serie base
        #'time'     tempo accumulato (secondi)          # possibile serie base
        #'asc'      ascesa accumulata (metri o feet)    # possibile serie base
        #'dis'      discesa accumulata (metri o feet)   # possibile serie base
        #'vel'      velocita' istantanea (km/h mi/h)    # possibile serie base
        
        lat_serie = []
        lon_serie = []
        ele_serie = []
        dist_serie = []
        time_serie = []
        asc_serie = []
        dis_serie = []
        vel_ist = []
        
        total_dist = 0
        this = datetime.datetime.now()
        total_tempo = this - this
        total_climb = 0
        total_slope = 0
        result = []
        if self.baseSerie:
            last_ele = self.baseSerie[0]['ele']
            #print self.baseSerie[:5]
            for row in self.baseSerie:
                # calcola distanza le serie per la 
                # distanza accumulata
                # tempo accumulato
                # ascesa accumulato
                # discesa accumulato
                # lascia inalterato lat, lon, ele                
            
                ele         = row['ele']
                delta_ele = ele - last_ele
                last_ele = ele
                if delta_ele >= 0:
                    total_climb += delta_ele
                else:   
                    total_slope += abs(delta_ele)
                    
                total_dist += row['delta_dist']
                total_tempo += row['delta_time'] 
                
                lat_serie.append(row['lat'])
                lon_serie.append(row['lon'])
                ele_serie.append(ele)
                dist_serie.append(total_dist)
                time_serie.append(total_tempo.seconds) # valore in secondi
                asc_serie.append(total_climb)
                dis_serie.append(total_slope)
                vel_ist.append(row['delta_dist']/ (row['delta_time'].seconds / 3600.0) )
                
                    
        result = {
                    'lat':lat_serie,
                    'lon':lon_serie,
                    'ele':ele_serie,
                    'dist':dist_serie,
                    'time':time_serie, 
                    'asc':asc_serie,
                    'dis':dis_serie,
                    'vel':vel_ist,
                 }
        return result
    
    def handleTrackFile(self, dom) :
        points = dom.getElementsByTagName("trkpt")
        
        # calcola la massima e minima elevazione
        self._max_min_ele(points)
        
        for i in range (0, len(points), 1) :
            self.handleTrackPoint(points[i])
        self.accumulate_climb(0)
        

# PER FUTURI SVILUPPI
# GDAL library necessaria
#utm2epsg = {"54N": 3185, ...}
"""
from django.geowork.gis.geos import Point ## da errore di importazione modulo

def wgs84_2_utm(lat, lon):
    p = Point(lon, lat, srid=4326) # 4326 = WGS84 epsg code
    p.transform(32633)
    lon, lat = p.get_coords()
    return lat, lon
"""