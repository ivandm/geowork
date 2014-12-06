# -*- coding: ISO-8859-1 -*-
"""
Form Widget classes specific to the geoSite admin site.
"""
###########
# WIDGETS #
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
###########

# A class that corresponds to an HTML form widget, 
# e.g. <input type="text"> or <textarea>. 
# This handles rendering of the widget as HTML.
import json

from django.forms import widgets, MultiWidget, Media
from django.utils.html import conditional_escape, format_html, format_html_join
from django.forms.util import flatatt, to_current_timezone
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from geowork.geometric import LatLng
from geowork.compass import createCompass, Compass
from geowork.imageComposer import ImageComposerManager

class CommonMedia(object):
    """
        Class CommonMedia
        Utilizzare questa classe per tutti i fle css e js comuni
        
        Attributi:
            _css: un dizionario
            _js: una lista di 
            
        Metodi:
            css(*new_css)
            js(new_js)
            
            "Ritornano una tupla con i valori comuni piu' quelli passati"
    """
    _css = {
            'all': ['marks/jquery-ui.min.css', 'marks/jquery-ui.min.css',
            #'marks/css/font-a2i.css',
            ]
    }
    _js = [
          # ??? utilizzando SOLO qui googleapis non funzione google.maps.places.SearchBox nell'admin site
          # se invece googleapis viene inserito nell'<head> tutto ok
          #'https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&sensor=false&key=AIzaSyB22J57AckpUOa1up4Zp2c1MUDTzu3UMEM',
          'marks/jquery.min.js', 'marks/jquery-ui.min.js',
          'marks/wrapperGoogleMaps.js','marks/mappe.js',  
        ] 

    def css(self,  media_type, *new_css):
        if self._css.has_key(media_type):
            total_css = self._css[media_type] + list(new_css)
        else:
            total_css = new_css
        return tuple(total_css)
    
    def js(self, *new_js):
        total_js = self._js + list(new_js)
        return tuple(total_js)
    
class SeasonField(widgets.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super(SeasonField, self).__init__(*args, **kwargs)
        
    def render(self, name, value, attrs=None, choices=()):
        has_compass = False
        if isinstance(value, ImageComposerManager):
            compass_obj = value
            value = compass_obj.composerList
            has_compass = True
        out = super(SeasonField, self).render(name, value, attrs=None, choices=())    
        if value and has_compass:
            img = '<div><img src="/%(path)s" alt="" height="%(h)s" width="%(w)s"></div>'
            img_obj = compass_obj.image
            defaultW = 100
            defaultH = 100
            img_attr = {
                'path':     img_obj.path_name,
                'w':        defaultW,           #img_obj.w,
                'h':        defaultH,           #img_obj.h
            }
            out = out + mark_safe( img % img_attr )
        return out

class CompassWidget(widgets.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super(CompassWidget, self).__init__(*args, **kwargs)
        
    def render(self, name, value, attrs=None, choices=()):
        has_compass = False
        if isinstance(value, Compass):
            compass_obj = value
            value = compass_obj.esposition
            has_compass = True
        out = super(CompassWidget, self).render(name, value, attrs=None, choices=())
        if value and has_compass:
            img = '<div><img src="/%(path)s" alt="" height="%(h)s" width="%(w)s"></div>'
            img_obj = compass_obj.image
            defaultW = 100
            defaultH = 100
            img_attr = {
                'path':     img_obj.path_name,
                'w':        defaultW,           #img_obj.w,
                'h':        defaultH,           #img_obj.h
            }
            out = out + mark_safe( img % img_attr )
        return out
    
    
class GpxFieldWidget(widgets.ClearableFileInput):

    class Media:
        #extend = True
        css = {
            'all': CommonMedia().css('all', 'marks/style.css',)
        }
        js = CommonMedia().js('marks/track.js', 'marks/dygraph-combined.js', 
        #'marks/highcharts/highcharts.js', 'marks/highcharts/modules/data.js', 'marks/highcharts/modules/exporting.js',
        #'marks/highcharts.js',
        #'marks/graphMaker.js',
            ) 
                
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        
        substitutions['input'] = super(GpxFieldWidget, self).render(name, None, attrs)

        if value and hasattr(value, "url"):
            
            substitutions['input_text'] = _(u'Change')
            template ='%(contribute)s - <br />%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
            #template_with_graphs ='%(contribute)s - %(graphics)s - %(graphics1)s - <br />%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
            
            template_maxmin = """<div class="fa2i_altitude_container"><div class="fa2i "><img class="" src="{% static 'marks/web_images/maxmin86x36.png' %}" alt="" height='40'><div class="fa2i fa2i_altitude_top">%(max)s</div><div class="fa2i fa2i_altitude_bottom">%(min)s</div></div></div>"""	
                        
            contribute_button = u'<button {0}">%s</button>'%_('Traccia sulla mappa') 
            urlRequest_destHtml = [
                                   {'url':'/marks/track_on_map/'+value.url,
                                    'html':'map_track'
                                   },
                                   {'url':'/marks/graphs/get_graphs',
                                    'html':'map_graph'}
                                    ]
            contribute = format_html( 
                        contribute_button, 
                        flatatt({
                            'id':'geoTrack',
                            'class': 'geoButton',
                            'urlRequest_destHtml': '/marks/track_on_map/'+value.url,
                            'urlRequest_destHtml_test': json.dumps(urlRequest_destHtml),
                             })
                        )
            
            graph_template = u'<a href="{0}"><img src="{1}" width="{2}" /></a>'
            #graphics = format_html( graph_template, "/marks/getgraph/%s?system=m&type=profile" % force_text(value), "/marks/getgraph/%s?system=m&type=profile" % force_text(value), 200 )
            #graphics1 = format_html( graph_template, "/marks/getgraph/%s?system=m&type=maxmin" % force_text(value), "/marks/getgraph/%s?system=m&type=maxmin" % force_text(value), 200 )
                 
            substitutions['contribute'] = contribute
            #substitutions['graphics'] = graphics
            #substitutions['graphics1'] = graphics1
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   '/'+value.url,
                                                   force_text(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
                
    
# classe widget utilizzata dal campo forms.geoFields LatLngField
class LatLngTextInputWidget(widgets.TextInput):
    """
    LatLngTextInputWidget
    
    Parametri html extra per il pulsante
    
    LatLngTextInputWidget(marker_extra_attrs=dict(class='test_class', html='Setta Marker'))
    
    <button type="button" class=" [class] "> [html] </button>
    """

    def __init__(self, *args, **kwargs):       
        super(LatLngTextInputWidget, self).__init__( *args, **kwargs)
    class Media(CommonMedia):
        #extend = False
        css = {
            'all': CommonMedia().css('all', 'marks/style.css',)
        }
        js = CommonMedia().js('marks/actions.js', 'marks/sincro.js') 

    def render(self, name, value, attrs=None):
        # chiamata per visualizzare HTML
        # ritorna un campo input text e un campo button
        # con entrambe attributo id='form_id-%#-%s'
        # dove %# e' il numero consecutivo del campo
        # dove %s e' il nome del campo db field generato
        
        #out = super(LatLngTextInputWidget, self).render(name, value, attrs)
        
        input_attrs = {}
        if value is None:
            value = ''

        p = LatLng()
        lenght = len(p)
        default = {'size': lenght, 'maxlength': lenght, 'class': 'geoMark' }
        attrs.update(default)
        input_attrs.update({'id': attrs['id'],
                            
                            })
        
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))

        marker_attrs = {
                'html':  _(u"Inserisci dalla Mappa"),
                'class': 'geoMark',
                }
        button_text = u'<button type="button" {0} class="%s">%s</button>' % (
                                                    marker_attrs['class'],
                                                    marker_attrs['html'],
                                                    )
        input_attrs_button = input_attrs
        input_attrs_button['id'] = attrs['id']
        button = format_html( button_text, flatatt(input_attrs_button) )
        tag = '<input{0} />'+button
        return format_html(tag, flatatt(final_attrs))
        #return super(LatLngTextInputWidget, self).render(name, value, attrs)

######################################################        
# TODO: le seguenti classi serviranno forse in futuro
######################################################
class LatLngInputWidget(widgets.Input):
    pass
    
class LatLngWidget(MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            LatLngTextInputWidget(),
            LatLngInputWidget(),
        )
        super(LatLngWidget, self).__init__(_widgets, attrs)
        
    def decompress(self, value):
        if value is None:
            value = ['', '']
        else:
            value = [value.to_string(), '']
        return value