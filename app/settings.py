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


""" database setting file. """


import sys,glob,os,pickle,string
import numpy as np
from netCDF4 import Dataset,num2date
import pandas as pd
import pycountry

# ISOs that can be chosen
all_isos=['AGO', 'DZA', 'EGY', 'GNQ', 'BEN', 'NGA', 'NER', 'ZWE', 'NAM', 'GNB', 'SWZ', 'GHA', 'COG', 'SLE', 'ETH', 'COM', 'ERI', 'CPV', 'LBR',\
            'LBY', 'LSO', 'UGA', 'RWA', 'SOM', 'MDG', 'CMR', 'TZA', 'BWA', 'SEN', 'TCD', 'GAB', 'BFA', 'MWI', 'MOZ', 'MRT', 'GMB', 'MLI', 'BDI', \
            'STP', 'DJI', 'GIN', 'ESH', 'KEN', 'MAR', 'COD', 'ZMB', 'ZAF', 'TGO', 'TUN', 'CAF', 'SSD', 'SDN', 'CIV','SYC','MUS']

all_isos=list(set([filename.split('/')[-1].split('_')[0] for filename in glob.glob('app/static/plots_maps/*')]))

# find french country names
iso_fr=open('app/iso_french_country.txt','r').read().split('\n')
french_cou_dict={}
for line in iso_fr:
    if len(line)>1:
        french_cou_dict[line.split('\t')[2][0:3]]=line.split('\t')[0]
french_cou_dict['ESH']='Sahara occidental'

# create a dict for country names. For english names, the python package pycountry is used
country_names={}
for iso in all_isos:
	country_names[iso]={'en':pycountry.countries.get(alpha_3=iso).name,'fr':french_cou_dict[iso]}

# read result table
result=pd.read_csv('app/static/data/isimip_cropimpact_warmlevel_deltaval.csv',sep=';')
result['Crop'][result['Crop']=='soy']='soybean'
result['Country'][result['Country']=='Congo_DemRep']='Congo, The Democratic Republic of the'
result['Country'][result['Country']=='Cote_d_Ivoire']="Côte d'Ivoire"
result['Country']=[cou.replace('_',' ') for cou in result['Country']]

result['delta.yield.median']=[int(round(num)) for num in result['delta.yield.median']*100]
result['delta.yield.Q1']=[int(round(num)) for num in result['delta.yield.Q1']*100]
result['delta.yield.Q3']=[int(round(num)) for num in result['delta.yield.Q3']*100]
result['Area']=[int(round(num)) for num in result['Area']]

result_other=pd.read_csv('app/static/data/isimip_cropimpact_warmlevel_deltaval_othercrops.csv',sep=';')
result_other['Crop'][result_other['Crop']=='soy']='soybean'
result_other['Country'][result_other['Country']=='Congo_DemRep']='Congo, The Democratic Republic of the'
result_other['Country'][result_other['Country']=='Cote_d_Ivoire']="Côte d'Ivoire"
result_other['Country']=[cou.replace('_',' ') for cou in result_other['Country']]

result_other['delta.yield.median']=[int(round(num)) for num in result_other['delta.yield.median']*100]
result_other['delta.yield.Q1']=[int(round(num)) for num in result_other['delta.yield.Q1']*100]
result_other['delta.yield.Q3']=[int(round(num)) for num in result_other['delta.yield.Q3']*100]
result_other['Area']=[int(round(num)) for num in result_other['Area']]

# indicators, units, timesteps, long names
ind_dict={
    'maize':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'wheat':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'soybean':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'rice':{'unit':'t ha-1 yr-1','time_step':'yearly'},
}

# names of indicators
indicator_dict={'fr':{
    'maize':'Rendement du maïs',
    'wheat':'Rendement du blé',
    'soybean':'Rendement du soja',
    'rice':'Rendement du riz',
	},
	'en':{
    'maize':'maize yield',
    'wheat':'wheat yield',
    'soybean':'soy yield',
    'rice':'rice yield',
	}
}

# names of indicators
indicator_short_dict={'fr':{
    'maize':'maïs',
    'wheat':'blé',
    'soybean':'soja',
    'rice':'riz',
    'millet':'millet',
    'groundnut':'arachide',
    'beans':'haricots',
    'cassava':'manioc',
    'sorghum':'sorgho',
    'cotton':'coton',
    'peas':'pois',
    'sugarcane':'canne à sucre',
    'sunflower':'tournesol'
	},
	'en':{
    'maize':'maize',
    'wheat':'wheat',
    'soybean':'soy',
    'rice':'rice',
    'millet':'millet',
    'groundnut':'groundnut',
    'beans':'beans',
    'cassava':'cassava',
    'sorghum':'sorghum',
    'cotton':'cotton',
    'peas':'peas',
    'sugarcane':'sugarcane',
    'sunflower':'sunflower'
	}
}


# some french and english dictionaries
# there might be smoother way to deal with translations
# this seemed to be the easiest to me, but maybe it's not...

form_labels={'fr':{
	'country':u'Pays analysé:',
	'region':u'Région administrative:',
	'scenario':u"Scénario d'émission:",
	'indicator':u'Indicateur climatique:',
	},'en':{
	'country':u'Studied country:',
	'region':u'Administrative region:',
	'scenario':u'Emission scenario:',
	'indicator':u'Climate indicator:',
	}

}


warming_lvl_dict={'en':{
	'1p0':'+1.0°C',
	'1p5':'+1.5°C',
	'2p0':'+2.0°C',
    '2p5':'+2.5°C',
    '3p0':'+3.0°C',
},'fr':{
	'1p0':'+1.0°C',
	'1p5':'+1.5°C',
	'2p0':'+2.0°C',
    '2p5':'+2.5°C',
    '3p0':'+3.0°C',
}
}


print 'done with settings'
