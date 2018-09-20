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

import os,glob,sys,time
from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask, send_from_directory
from werkzeug.routing import BuildError
import pandas as pd
import pycountry


import forms

import settings
ind_dict=settings.ind_dict
indicator_dict=settings.indicator_dict
form_labels=settings.form_labels
warming_lvl_dict=settings.warming_lvl_dict
languages={'en':'English'}

result=settings.result
result_other=settings.result_other

# # not used, but could be useful
# def flash_errors(form):
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(u"Error in the %s field: %s" % (
#                 getattr(form, field).label.text,
#                 error
#             ))




@app.route('/')
def index():
    '''
    this function initializes all session arguments
    it should be the first page a user accesses
    '''

    # delete session files older than an hour
    os.system('find app/static/COU_sessions/ -type f -mmin +60 -delete')

    session['language']='en'

    # the following lines load lists of indicators, countries etc from settings and set the default parameters (SEN, tas etc.)
    session["country_avail"]   = sorted(settings.country_names.keys())
    session['country']   = session["country_avail"][0]
    session['country']   = 'BEN'

    # for filename in glob.glob('app/static/plots_maps/'+session['country']+'*'):
    #     print(filename)
    #     print(filename.split('/')[-1].split('_')[1])

    session["indicator_avail"] = list(set([filename.split('/')[-1].split('_')[1] for filename in glob.glob('app/static/plots_maps/'+session['country']+'*') if len(filename.split('/')[-1].split('_'))>1]))
    session["indicator"]   = session["indicator_avail"][0]
    index=session['indicator_avail'].index(session['indicator'])
    session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]

    session["warming_lvl_avail"]   = ['1p0','1p5','2p0','2p5','3p0']
    session["warming_lvl"]   = '1p5'
    index=session['warming_lvl_avail'].index(session['warming_lvl'])
    session['warming_lvl_avail'][index],session['warming_lvl_avail'][0]=session['warming_lvl_avail'][0],session['warming_lvl_avail'][index]


    session['location']='index'
    return redirect(url_for("choices"))

@app.route('/choices')
def choices():
    '''
    This is the main function - preparing choices_en.html or choices_fr.html
    '''
    # try if everything goes smooth, if anything is not working, redirect to some error page
    # try:
    if True:
        # define local variables for convenience
        s=session
        lang=s['language']
#        region=s['region']

        # fill the form for country choice
        form_country = forms.countryForm(request.form)
        s["country_avail"]   = sorted(settings.country_names.keys())
        s['country_avail']=[s['country']]+[co for co in s['country_avail'] if co != s['country']]
        form_country.countrys.choices = zip(s['country_avail'],[settings.country_names[cou][lang] for cou in s['country_avail']])

        # fill indicator forms - restrict for small regions
        form_indicator = forms.indicatorForm(request.form)
        s['indicator_avail']=[s['indicator']]+[ind for ind in s['indicator_avail'] if ind != s['indicator']]
        form_indicator.indicators.choices = zip(s['indicator_avail'],[indicator_dict[lang][ind][0].upper()+indicator_dict[lang][ind][1:] for ind in s['indicator_avail']])

        # fill the form for the warming level choice
        form_warming_lvl = forms.warming_lvlForm(request.form)
        s['warming_lvl_avail']=[s['warming_lvl']]+[wlvl for wlvl in s['warming_lvl_avail'] if wlvl != s['warming_lvl']]
        form_warming_lvl.warming_lvls.choices = zip(s['warming_lvl_avail'],[warming_lvl_dict[lang][wlvl][0].upper()+warming_lvl_dict[lang][wlvl][1:] for wlvl in s['warming_lvl_avail']])

        # get country table snippet
        result_snippet=result.loc[(result['Country']==pycountry.countries.get(alpha_3=s['country']).name) & (result['Irrigation']=='actual') & (result['CO2']=='co2')]

        result_snippet_other=result_other.loc[(result_other['Country']==pycountry.countries.get(alpha_3=s['country']).name) & (result_other['Irrigation']=='actual') & (result_other['CO2']=='co2')]

        # the following dicts will fill gaps in choices_en.html with text corresponding to the choices made by the user
        # I'm not sure if this is the most elegant way
        context={
            'hist_map':'static/plots_maps/'+s['country']+'_'+s['indicator']+'_total_hist.png',
            'proj_map':'static/plots_maps/'+s['country']+'_'+s['indicator']+'_total_'+s['warming_lvl']+'.png',
            'irr_added_value_map':'static/plots_maps/'+s['country']+'_'+s['indicator']+'_irr-added-value_'+s['warming_lvl']+'.png',
    #        'proj_co2_boxplot':'static/plots_boxplot/'+'plot_delta_yield_actual_co2_'+settings.country_names[s['country']]['en']+'.png',
    #        'proj_noco2_boxplot':'static/plots_boxplot/'+'plot_delta_yield_actual_noco2_'+settings.country_names[s['country']]['en']+'.png',

            'form_country':form_country,
            'form_indicator':form_indicator,
            'form_warming_lvl':form_warming_lvl,

            'result_snippet':result_snippet.round(2),
            'result_snippet_other':result_snippet_other.round(2),
            'crops':set(result_snippet['Crop']),
            'crops_other':set(result_snippet_other['Crop']),

            'indicator':indicator_dict[lang][s['indicator']],
        }

        session['location']='choices'
        return render_template('choices_'+lang+'.html',**context)
    #
    # except Exception,e:
    #     print str(e)
    #     return render_template('error.html')



###############################
# Define Season
###############################

###############################
# option choices
###############################
@app.route('/country_choice',  methods=('POST', ))
def country_choice():
  form_country = forms.countryForm(request.form)
  session['country']=form_country.countrys.data
  session["indicator_avail"] = list(set([filename.split('/')[-1].split('_')[1] for filename in glob.glob('app/static/plots_maps/'+session['country']+'*') if len(filename.split('/')[-1].split('_'))>1]))
  session["indicator"]   = session["indicator_avail"][0]

  return redirect(url_for('choices'))

@app.route('/indicator_choice',  methods=('POST', ))
def indicator_choice():
  form_indicator = forms.indicatorForm(request.form)
  session['indicator']=form_indicator.indicators.data

  return redirect(url_for('choices'))

@app.route('/warming_lvl_choice',  methods=('POST', ))
def warming_lvl_choice():
  form_warming_lvl = forms.warming_lvlForm(request.form)
  session['warming_lvl']=form_warming_lvl.warming_lvls.data

  return redirect(url_for('choices'))

###############################
# Download
###############################

###############################
# Navigation
###############################
def get_language_tag():
  if session['language']=='fr':
    return(languages['en'])
  if session['language']=='en':
    return(languages['fr'])

@app.route('/language_choice',  methods=('POST', ))
def language_choice():
  if session['language']=='en': lang=0
  if session['language']=='fr': lang=1
  lang*=-1
  session['language']=['en','fr'][lang+1]
  return redirect(url_for(session['location']))

@app.route('/go_to_choices',  methods=("POST", ))
def go_to_choices():
  return redirect(url_for("choices"))

@app.route('/home',  methods=('GET', ))
def render_home():
  return redirect(url_for('index'))

@app.route('/about',  methods=('GET', ))
def render_about():
  return render_template('about.html')

@app.route('/contact',  methods=('GET', ))
def render_contact():
  return render_template('contact.html')

@app.route('/documentation')
def documentation():
  session['location']='documentation'
  return render_template('documentation_'+session['language']+'.html',language=get_language_tag())

@app.route('/download_plot/<request>',  methods=('GET',"POST", ))
def download_plot(request):
  print request
  return send_from_directory(directory='static/plots_maps/', filename=request.replace('png','pdf'),as_attachment=True)

@app.route('/download_data',  methods=('GET',"POST", ))
def download_data():
  print request
  result_snippet=result.loc[(result['Country']==pycountry.countries.get(alpha_3=session['country']).name) & (result['Irrigation']=='actual') & (result['CO2']=='co2')]
  result_snippet.to_csv('app/static/data/'+session['country']+'.csv',sep=';')
  return send_from_directory(directory='static/data/', filename=session['country']+'.csv',as_attachment=True)

@app.route('/download_data_other',  methods=('GET',"POST", ))
def download_data_other():
  print request
  result_snippet_other=result_other.loc[(result_other['Country']==pycountry.countries.get(alpha_3=session['country']).name) & (result_other['Irrigation']=='actual') & (result_other['CO2']=='co2')]
  result_snippet_other.to_csv('app/static/data/'+session['country']+'_other.csv',sep=';')
  return send_from_directory(directory='static/data/', filename=session['country']+'_other.csv',as_attachment=True)

# @app.route('/user_type_choice',  methods=('POST', ))
# def user_type_choice():
#   if session['user_type']=='beginner': usr=0
#   if session['user_type']=='advanced': usr=1
#   usr*=-1
#   session['user_type']=['beginner','advanced'][usr+1]
#   if session['user_type']=='advanced':
#     print 'asdasdasd ------- asdas'
#     session['period_avail']=settings.periods_advanced
#   if session['user_type']=='beginner':
#     session['period_avail']=settings.periods_beginner
#     session['dataset']='CORDEX_BC'
#   return redirect(url_for('choices'))

# @app.route('/go_to_model_agreement',  methods=("POST", ))
# def go_to_model_agreement():
#   return redirect(url_for("model_agreement"))

# @app.route('/go_to_bias_correction',  methods=("POST", ))
# def go_to_bias_correction():
#   return redirect(url_for("bias_correction"))

# @app.route('/model_agreement')
# def model_agreement():
  # try:
#     country=session['country']

#     form_period = forms.periodForm(request.form)
#     form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

#     refP = "-".join(str(t) for t in session["ref_period"])
#     proP = session['period']
#     periods={'ref':session["ref_period"],'projection':session["proj_period"]}
#     CORDEX_BC_plot_detail='static/images/'+country+'/'+session["indicator"]+'_'+session["scenario"]+'_'+session['dataset']+'_'+session['season']+'_details.png'

#     context = {
#       'CORDEX_BC_plot_detail':CORDEX_BC_plot_detail,
#     }
#     return render_template('model_agreement.html',**context)

#   except KeyError:
#     return redirect(url_for("index"))

# @app.route('/bias_correction')
# def bias_correction():
  # try:
#     country=session['country']

#     form_period = forms.PeriodField(request.form)
#     form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

#     refP = "-".join(str(t) for t in session["ref_period"])
#     proP = session['period']
#     periods={'ref':session["ref_period"],'projection':session["proj_period"]}
#     bias_corretion_check='static/images/'+country+'/'+session["indicator"]+'_BC_check_'+session['season']+'.png'

#     context = {
#       'bias_corretion_check':bias_corretion_check
#     }
#     return render_template('bias_correction.html',**context)

#   except KeyError:
#     return redirect(url_for("index"))
