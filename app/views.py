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

import os,glob,sys,time,random,cPickle,string
from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask, send_from_directory
from collections import OrderedDict
from werkzeug.routing import BuildError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)

# load RegioClim scripts
sys.path.append(basepath+'RegioClim')
import country_analysis; reload(country_analysis)
import forms
from plotting import *

import settings
ind_dict=settings.ind_dict
indicator_dict=settings.indicator_dict
season_dict=settings.season_dict
form_labels=settings.form_labels
text_dict=settings.text_dict
button_dict=settings.button_dict
warming_lvl_dict=settings.warming_lvl_dict
languages={'en':'English','fr':'Français'}

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

    session["ref_period"]   = settings.ref_period
    session["proj_period"]  = settings.proj_period

    session['use_periods'] = True

    session['warming_lvl_avail']=warming_lvl_dict['en'].keys()
    session['warming_lvl']='2.0'
    session['warming_lvl_ref']='ref'
    index=session['warming_lvl_avail'].index(session['warming_lvl'])
    session['warming_lvl_avail'][index],session['warming_lvl_avail'][0]=session['warming_lvl_avail'][0],session['warming_lvl_avail'][index]

    session["scenario_avail"]   = settings.scenarios
    session["scenario"]   = settings.scenarios[0]

    session["dataset_avail"]   = settings.datasets
    session["dataset"]   = settings.datasets[0]

    session["indicator_avail"]   = ['tas','TXx','pr','RX1','year_RX5']
    session["indicator"]   = 'tas'
    index=session['indicator_avail'].index(session['indicator'])
    session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]

    session['small_region_warning']=False

    session['ref_period_warning']='ok'
    session['proj_period_warning']='ok'

    session["season_avail"]   = settings.seasons.keys()
    session["season"]   = 'year'

    session['new_season_name']=''
    session['new_season_name_auto']=True

    session['id']=str(int((time.time()-int(time.time()))*10000))+str(int(random.random()*100000))
    session['cou_path']='app/static/COU_sessions/'+session['id']+'_'+session['country']+'.pkl'


    session["region_avail"]   = ['asdas','asdas']
    session['region']   = session["region_avail"][0]

    session['new_region_name']=''
    session['new_region_name_auto']=True

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
        region=s['region']

        # fill the form for country choice
        form_country = forms.countryForm(request.form)
        s["country_avail"]   = sorted(settings.country_names.keys())
        s['country_avail']=[s['country']]+[sea for sea in s['country_avail'] if sea != s['country']]
        form_country.countrys.choices = zip(s['country_avail'],[settings.country_names[cou][lang] for cou in s['country_avail']])

        # fill the form of region choice - a bit complicated sorting
        form_region = forms.regionForm(request.form)
        sorted_regions = ['asdas','asdasas']
        sorted_regions=[s['region']]+[reg for reg in sorted_regions if (reg != s['region']) & ('+' in reg)]+[reg for reg in sorted_regions if (reg != s['region']) & ('+' not in reg)]
        form_region.regions.choices = zip(sorted_regions,['sdsad','asdasd'])

        # fill scenario forms
        form_scenario = forms.scenarioForm(request.form)
        form_scenario.scenarios.choices = zip(s['scenario_avail'],s['scenario_avail'])

        # form_dataset = forms.datasetForm(request.form)
        # form_dataset.datasets.choices = zip(s['dataset_avail'],s['dataset_avail'])

        # fill indicator forms - restrict for small regions
        form_indicator = forms.indicatorForm(request.form)
        if s['small_region_warning']:
            indi_avail_tmp=['tas','pr']
        else:
            indi_avail_tmp=s['indicator_avail']
        form_indicator.indicators.choices = zip(indi_avail_tmp,[indicator_dict[lang][ind][0].upper()+indicator_dict[lang][ind][1:] for ind in indi_avail_tmp])

        # warming level forms
        form_warming_lvl = forms.warming_lvlForm(request.form)
        s['warming_lvl_avail']=[warming_lvl_dict[lang].keys()[warming_lvl_dict[lang].values().index(name)] for name in sorted(warming_lvl_dict[lang].values())]
        s['warming_lvl_avail']=[s['warming_lvl']]+[sea for sea in s['warming_lvl_avail'] if sea not in [s['warming_lvl'],'ref']]
        form_warming_lvl.warming_lvls.choices = zip(s['warming_lvl_avail'],[warming_lvl_dict[lang][sea] for sea in s['warming_lvl_avail']])

        form_warming_lvl_ref = forms.warming_lvl_refForm(request.form)
        s['warming_lvl_avail']=[warming_lvl_dict[lang].keys()[warming_lvl_dict[lang].values().index(name)] for name in sorted(warming_lvl_dict[lang].values())]
        s['warming_lvl_avail']=[s['warming_lvl_ref']]+[sea for sea in s['warming_lvl_avail'] if sea not in [s['warming_lvl_ref'],'2.0']]
        form_warming_lvl_ref.warming_lvl_refs.choices = zip(s['warming_lvl_avail'],[warming_lvl_dict[lang][lvl] for lvl in s['warming_lvl_avail']])

        # period forms
        form_period = forms.PeriodField(request.form)
        ref_P = str(s["ref_period"][0])+'-'+str(s["ref_period"][1]-1)
        proj_P = str(s["proj_period"][0])+'-'+str(s["proj_period"][1]-1)
        form_period = forms.PeriodField(request.form, proj_period=proj_P, ref_period=ref_P)

        # season forms
        form_season = forms.seasonForm(request.form)
        s['season_avail']=['year']+ [sea for sea in sorted(season_dict[lang].keys()) if (sea not in ['year','10','11','12']) & ('+' not in sea)]+['10','11','12']+[sea for sea in sorted(season_dict[lang].keys()) if '+' in sea]
        s['season_avail']=[s['season']]+[sea for sea in s['season_avail'] if sea != s['season']]
        form_season.seasons.choices = zip(s['season_avail'],[season_dict[lang][sea] for sea in s['season_avail']])

        # prepare periods
        if s['use_periods']:
            # periods set by years
            refP = str(s["ref_period"][0])+'to'+str(s["ref_period"][1]-1)
            refP_longname=str(s["ref_period"][0])+'-'+str(s["ref_period"][1]-1)
            refP_clim=refP
            refP_clim_longname=refP_longname
            proP=str(s["proj_period"][0])+'to'+str(s["proj_period"][1]-1)
            proP_longname=str(s["proj_period"][0])+'-'+str(s["proj_period"][1]-1)
            periods={refP:s["ref_period"],proP:s["proj_period"]}
            periods_ewembi={refP:s["ref_period"]}

        else:
            # periods set by warming levels
            refP = s['warming_lvl_ref']
            refP_longname=warming_lvl_dict[lang][refP]
            refP_clim = 'ref'
            refP_clim_longname=warming_lvl_dict[lang]['ref']
            proP = s['warming_lvl']
            proP_longname=warming_lvl_dict[lang][proP]
            periods=COU._warming_slices
            periods_ewembi={'ref':[1986,2006]}

        # plot_context is a dictionary combing all information needed by plotting functions in plotting.py
        indicator_label=indicator_dict[lang][s['indicator']]+' ['+ind_dict[s['indicator']]['unit']+']'
        plot_context={
            's':s,
            'COU':'sdasd',
            'periods':periods,
            'periods_ewembi':periods_ewembi,
            'refP':refP,
            'refP_clim':refP_clim,
            'proP':proP,
            'refP_longname':refP_longname,
            'refP_clim_longname':refP_clim_longname,
            'proP_longname':proP_longname,
            'region':region,
            'lang':lang,
            'indicator_label':indicator_label[0].upper()+indicator_label[1:],
            'season_dict':season_dict,
            'highlight_region':region,
            'out_format':'_small.png'
        }

        # create all plots - see plotting.py
        EWEMBI_plot='path/to/plot'
        Projection_plot='path/to/plot'
        transient_plot='path/to/plot'
        annual_cycle_plot='path/to/plot'
        overview_plot='path/to/plot'
        plt.close('all'); plt.clf()
        print 'everything plotted '+str(time.time()-start_time)

        # the following dicts will fill gaps in choices_en.html with text corresponding to the choices made by the user
        # I'm not sure if this is the most elegant way
        plot_dict={
            'EWEMBI_plot':EWEMBI_plot.replace('app/',''),
            'Projection_plot':Projection_plot.replace('app/',''),
            'transient_plot':transient_plot.replace('app/',''),
            'annual_cycle_plot':annual_cycle_plot.replace('app/',''),
            'overview_plot':overview_plot.replace('app/',''),
        }

        if s['season']=='year':season_add_on=''
        if s['season']!='year' and lang=='en':season_add_on=' in '+season_dict[lang][s['season']]
        if s['season']!='year' and lang=='fr':season_add_on=' en '+season_dict[lang][s['season']]

        if s['use_periods']==False:
            refP_clim_longname=refP_clim_longname.replace('°C','°C '+settings.above_preindustrial[lang])
            refP_longname=refP_longname.replace('°C','°C '+settings.above_preindustrial[lang])
            proP_longname=proP_longname.replace('°C','°C '+settings.above_preindustrial[lang])

        plot_text_dict={
            'indicator':indicator_dict[lang][s['indicator']],
            'season_add_on':season_add_on,
            'refP_longname':refP_longname,
            'proP_longname':proP_longname,
            'refP_clim_longname':refP_clim_longname,
        }

        other_dict={
            'language':get_language_tag(),
            'use_periods':s['use_periods'],
            'small_region_warning':s['small_region_warning'],
            'ref_period_warning':s['ref_period_warning'],
            'proj_period_warning':s['proj_period_warning'],
            'language_flag':languages[s['language']],
        }

        form_dict = {
            'form_country':form_country,
            'form_region':form_region,
            'form_period':form_period,
            'form_warming_lvl':form_warming_lvl,
            'form_warming_lvl_ref':form_warming_lvl_ref,
            'form_season':form_season,
            'form_scenario':form_scenario,
            'form_indicator':form_indicator,
        }

        # all dicts are combined into one dict which is than passed to the template
        context=form_dict.copy()
        context.update(other_dict)
        context.update(plot_dict)
        context.update(plot_text_dict)
        context.update(text_dict[lang])
        context.update(button_dict[lang])

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
ute('/indicator_choice',  methods=('POST', ))
def indicator_choice():
  form_indicator = forms.indicatorForm(request.form)
  session['indicator']=form_indicator.indicators.data
  # put chosen at beginning of list
  session['indicator_avail']=['tas','TXx','pr','RX1','year_RX5']
  session['indicator_avail']=[session['indicator']]+[ind for ind in ['tas','TXx','pr','RX1','year_RX5'] if ind!=session['indicator']]
  #index=session['indicator_avail'].index(session['indicator'])
  #session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]
  if ind_dict[session['indicator']]['time_step']=='yearly':  session["season_avail"]=['year']
  if ind_dict[session['indicator']]['time_step']=='monthly':  session["season_avail"]=settings.seasons.keys()
  if session["season"] not in session["season_avail"]: session["season"] = 'year'
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
