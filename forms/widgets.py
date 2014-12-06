# -*- coding: ISO-8859-1 -*-
"""
Form Widget classes
"""
###########
# WIDGETS #
###########
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

from django.forms import widgets, MultiWidget, Media
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import ChoiceFieldRenderer, CheckboxChoiceInput
from django.utils.html import conditional_escape, format_html
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.safestring import mark_safe

from django.utils import formats, six
from django.forms.util import flatatt
from django.forms.widgets import TextInput
from datetime import timedelta


class DurationInput(TextInput):
    def render(self, name, value, attrs=None):
        """
        output.append(u'<li>%(cb)s<label%(for)s>%(label)s</label></li>' % {"for": label_for, "label": option_label, "cb": rendered_cb})
        """
        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            if isinstance(value, six.integer_types):
                value = timedelta(microseconds=value)

            # Otherwise, we've got a timedelta already

            final_attrs['value'] = force_text(formats.localize_input(value))
        return mark_safe('<input%s />' % flatatt(final_attrs))
        
        
class myImgCheckboxFieldRenderer(ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput
    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<ul id="{0}" class="multiple_cloumns double">', id_) if id_ else '<ul>'
        output = [start_tag]
        for i, choice in enumerate(self.choices):
            choice_value, choice_label = choice
            img = mark_safe('<img class="fac-background fac-%s"> </img>'%choice_value)
            if isinstance(choice_label, (tuple, list)):
                attrs_plus = self.attrs.copy()
                if id_:
                    attrs_plus['id'] += '_{0}'.format(i)
                sub_ul_renderer = ChoiceFieldRenderer(name=self.name,
                                                      value=self.value,
                                                      attrs=attrs_plus,
                                                      choices=choice_label)
                sub_ul_renderer.choice_input_class = self.choice_input_class
                output.append(format_html('<li>{0}{1}{2}</li>', force_text(img), choice_value,
                                          sub_ul_renderer.render()))
            else:
                w = self.choice_input_class(self.name, self.value,
                                            self.attrs.copy(), choice, i)
                
                output.append(format_html('<li>{0} {1}</li>', force_text(img), force_text(w)))
        output.append('</ul>')
        return mark_safe('\n'.join(output))
        
class myCheckboxSelectMultiple(CheckboxSelectMultiple):
    renderer = myImgCheckboxFieldRenderer
    
class DigitPercentWidget(widgets.NumberInput):
    class Media:
        css = {
            'all': ('',),
            }
        js = ('',)
    def render(self, name, value, attrs=None):
        original_html = super(DigitPercentWidget, self).render(name, value, attrs=attrs)
        
        print type(value), value
        if value:
            print
        return super(NumberInput, self).render(name, value, attrs=attrs)
# Text area widget con editor di testo WYSIWYG
class TextEditorField(widgets.Textarea):
    class Media:
        #extend = True
        css = {
            'all': ('marks/jquery-te-1.4.0.css',),
            }
        js = ('marks/jquery.min.js', 'marks/jquery-te-1.4.0.min.js', 
              'marks/texteditor.js',
              )
    
    def __init__(self, *args, **kwargs):
        kwargs.update({'attrs': {'class': 'a2i-editor'}})
        super(TextEditorField, self).__init__(*args, **kwargs)
        
    def render(self, name, value, attrs=None):
        return super(TextEditorField, self).render(name, value, attrs=None)