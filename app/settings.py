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
	if os.path.isdir('app/static/COU_images/'+iso)==False:os.system('mkdir app/static/COU_images/'+iso)
	country_names[iso]={'en':pycountry.countries.get(alpha_3=iso).name,'fr':french_cou_dict[iso]}

# read result table
result=pd.read_csv('app/static/data/isimip_cropimpact_warmlevel_deltaval.csv',sep=';')


# indicators, units, timesteps
ind_dict={
    'maize':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'wheat':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'soy':{'unit':'t ha-1 yr-1','time_step':'yearly'},
    'rice':{'unit':'t ha-1 yr-1','time_step':'yearly'},
}

# names of indicators
indicator_dict={'fr':{
    'maize':'rendement du maïs',
    'wheat':'rendement du blé',
    'soy':'rendement du soja',
    'rice':'rendement du riz',
	},
	'en':{
    'maize':'maize yield',
    'wheat':'wheat yield',
    'soy':'soy yield',
    'rice':'rice yield',
	}
}

# names of management practices
management_dict={'fr':{
    'all':'pluviale et irriguée',
    'noirr':'pluviale',
    'firr':'irriguée',
	},
	'en':{
    'all':'rainfed and irrigated',
    'noirr':'rainfed',
    'firr':'irrigated',
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

plot_titles={'en':{
	'EWEMBI_plot':u"Observations EWEMBI pour la période de réference 1986-2006",
	'CORDEX_plot':u"Projections de modèles cliamtiques",
	'transient_plot':u"",
	'annual_cycle_plot':u""
	},'fr':{
	'EWEMBI_plot':u"EWEMBI observations over the reference period 1986-2006",
	'CORDEX_plot':u"Change projected by regional climate modeles ",
	'transient_plot':u"",
	'annual_cycle_plot':u""
	}
}

# these are text fragments used in the templates
# this is defentively not elegant
text_dict={'en':{

	'country_h':'Country',
	'country_txt':'',

	'warning':'Warning: ',
	'warning_txt':'The chosen region is smaller than 5 grid-cells. Please ',
	'reduced_inidicator_set_txt':"The chosen region is smaller than 5 grid-cells. We don't provide extreme indicators for such small regions!",

	'merge_page_h':'Add another region',
	'merge_page_txt':'Select a region you want to add to the chosen region.',
	'warning_merge_page_txt':'The chosen region is smaller than 5 grid-cells. Please select another region you want to merge the current region with.',

	'warming_lvl_h':'Global Warming Level',
	'warming_lvl_txt_1':'Global warming level above pre-industrial for which the regional response is presented. Alternatively you can use ',
	'warming_lvl_txt_2':'',
	'future_warming_lvl':'Future warming level',
	'ref_warming_lvl':'Reference warming level',

	'indicator_h':'Climate Indicator',
	'indicator_txt':'Climate indicators based on daily temperature and precipitation. Please find more information about the indicators ',

},'fr':{

	'country_h':'Pays',
	'country_txt':'',

	'warning':'Avertissement!',
	'warning_txt':'La région choisie est plus petite que 5 grilles. Veuillez ',
	'reduced_inidicator_set_txt':"La région choisie est plus petite que 5 grilles. Nous ne fournissons pas d'indicateurs climatiques extrêmes pour cette région!",

	'merge_page_h':'Ajoutez une Région',
	'merge_page_txt':'Choisissez une région qui sera combiné avec la région actuelle.',
	'warning_merge_page_txt':'La région choisie est plus petite que 5 grilles. Veuillez choisir une autre région à combiner avec la région actuelle.',

	'warming_lvl_h':'Niveau de Réchauffement Global',
	'warming_lvl_txt_1':'Niveau de Réchauffement Global pour lequel la réponse climatique régionale est présentée. Vous pouvez aussi utiliser des ',
	'warming_lvl_txt_2':' pour lesquelles les projections climatiques seront projetées.',
	'future_warming_lvl':'Niveau de réchauffement future',
	'ref_warming_lvl':'Niveau de réchauffement de référence',

	'indicator_h':'Indicateur Climatique',
	'indicator_txt':'Indicateurs climatiques basés sur des donnés quotidiennes de température et de précipitation. Pour le moment aucun indicateur de sécheresse est présenté. Veuillez considérer les projection de précipitation pour les analyses de sécheresses en gardant à l`esprit que l`évapotranspiration potentielle pourrait augmenter avec la température.',

}
}

button_dict={'en':{
	'use_periods_0':'fixed time periods',
	'use_periods_1':'global warming levels',
	'merge_regions':'merge several regions.',
	'select_periods':'Select Periods',
	'define_season':'define a season.',
	'download_png':'Download png',
	'download_pdf':'Download pdf',
	'download_data':'Download data',
	'save_region':'Keep this Region',
	'save_season':'Keep this Season',

},'fr':{
	'use_periods_0':'périodes temporelles fixes',
	'use_periods_1':'niveau de réchauffement global',
	'merge_regions':'regrouper des régions.',
	'select_periods':'Choisir ces Périodes',
	'define_season':'définissez une saison.',
	'download_png':'Télécharger png',
	'download_pdf':'Télécharger pdf',
	'download_data':'Télécharger data',
	'save_region':'Garder cette Région',
	'save_season':'Garder cette Saison',
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
