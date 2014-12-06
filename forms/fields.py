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

from django import forms
from geowork.forms import widgets as formWidgets

from django.forms.fields import Field
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from geowork.forms.widgets import DurationInput
from geowork.utils.timestring import str_to_timedelta


class DurationField(Field):
    widget = DurationInput

    default_error_messages = {
        'invalid': _('Enter a valid duration.'),
    }

    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Returns a datetime.timedelta object.
        """
        super(DurationField, self).clean(value)
        try:
            return str_to_timedelta(value)
        except ValueError:
            raise ValidationError(self.default_error_messages['invalid'])

    def to_python(self, value):
        try:
            return str_to_timedelta(value)
        except ValueError:
            raise ValidationError(self.default_error_messages['invalid'])
            
class DigitPercentField(forms.DecimalField):
    widget = formWidgets.DigitPercentWidget
