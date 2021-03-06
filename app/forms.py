# -*- coding: utf-8 -*-

# Copyright (C) 2017 Peter Pfleiderer
#
# This file is part of regioclim.
#
# regioclim is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# regioclim is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with regioclim; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA




from wtforms import RadioField, SelectMultipleField, TextField, IntegerField, SelectField, StringField
from flask_wtf import Form,validators
from wtforms.validators import ValidationError, Required, Regexp


class countryForm(Form):
  countrys = SelectField(' ', choices=[],
            validators=[Required("Please select at least one region.")])

class indicatorForm(Form):
  indicators = SelectField(u'', choices=[],
            validators=[Required("Please select at least one region.")])

class warming_lvlForm(Form):
  warming_lvls = SelectField(u'', choices=[],
            validators=[Required("Please select at least one global warming level.")])

class managementForm(Form):
  managements = SelectField(u'', choices=[],
            validators=[Required("Please select at least one type of management practices.")])

class PeriodField(Form):
  regex = "[1-2][0-9]{3}-[1-2][0-9]{3}"

  ref_period    = TextField(u'', validators=[Regexp(regex, message="Please use YYYY-YYYY format.")])
  proj_period   = TextField(u'', validators=[Regexp(regex, message="Please use YYYY-YYYY format.")])

class NewRegionForm(Form):
  region_name    = TextField(u'region', validators=[Required()])

class NewSeasonForm(Form):
  season_name    = TextField(u'season', validators=[Required()])
