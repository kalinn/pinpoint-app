import random
import urllib
import os
from instagram.client import InstagramAPI
from flask import render_template, flash, redirect, session, request, url_for
from pinpoint import application
from .forms import cityForm
from .insta import getUrls, unauthenticated_api, CONFIG

CITIES_DICT_STR = os.environ['CITIESDICT']
CITIES_DICT_STR = CITIES_DICT_STR.replace('":"', '~')
CITIES_DICT_STR = CITIES_DICT_STR[2:-2]
CITIES_DICT_STR = CITIES_DICT_STR.split('", "')
ks = [l.split('~')[0] for l in CITIES_DICT_STR]
vs = [l.split('~')[1] for l in CITIES_DICT_STR]
CITIES_DICT = dict(zip(ks, vs))

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET'])
def index():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["basic"])
        return render_template('login.html', lnk=url)
    except Exception as e:
        print(e)

@application.route('/oauth_callback', methods=['GET', 'POST'])
def on_callback():
    code = request.args.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        if not session.has_key('access_token'):
            session['access_token'] = access_token
    except Exception as e:
        print(e)
    return redirect('/play')

@application.route('/play', methods=['GET', 'POST'])
def play():
    # If there is no city saved in the session, then upload a new random picture
    if not session.has_key('data'):
        allImg = []
        # Ensure enough pictures for guessing
        while len(allImg) < 4:
            firstCity, allImg = getUrls(session['access_token'])
        session['data'] = [firstCity, allImg]
    else:
        # Otherwise, use the saved city and random image from that city
        firstCity = session['data'][0]
        allImg = session['data'][1]
    if not session.has_key('allMsg'):
        allMsg = []
        session['allMsg'] = allMsg
    else:
        allMsg = session['allMsg']
    if not session.has_key('idx'):
        idx = 0
        session['idx'] = idx
        rImg = [allImg[idx]]
    else:
        idx = session['idx']
        rImg = allImg[0:(idx+1)]
    # User hasn't guessed correctly yet
    correct = False
    form = cityForm()
    if form.validate_on_submit():
        # Get user's guess
        cityGuess = str(form.city.data)
        # Convert to lower case with no spaces
        cityFmt = ''.join(str.split(cityGuess.lower()))
        if cityFmt.find(".")!=-1:
            newFmt = list(cityFmt)
            newFmt.pop(cityFmt.find("."))
            cityFmt = ''.join(newFmt)
        if firstCity==cityFmt:
            if not session.has_key('rImg'):
                session['rImg'] = rImg
            if not session.has_key('cityFmt'):
                session['cityFmt'] = cityFmt
            return redirect('/correct')
        if session['idx'] > 4:
            if not session.has_key('rImg'):
                session['rImg'] = rImg
            if not session.has_key('firstCity'):
                session['firstCity'] = firstCity
            return redirect('/wrong')
        # If they didn't guess correctly, session variables will keep track of the correct city and shown image on redirect
        else:
            allMsg.append(cityGuess)
            session['allMsg'] = allMsg
            for guess in allMsg:
                flash(guess)
            idx += 1
            session['idx'] = idx
            return redirect('/play')
    # This is what is rendered before form submit
    return render_template('index.html',
                           title='Pinpoint',
                           imageUrl=rImg,
                           form=form,
                           correct=correct,
                           lose=False,
                           corrCity=str(None))

@application.route('/correct', methods=['GET'])
def correct():
    if session.has_key('data'):
        del session['data']
    if session.has_key('idx'):
        del session['idx']
    if session.has_key('allMsg'):
        del session['allMsg']
    if session.has_key('firstCity'):
        del session['firstCity']
    # Remove session variables so new ones will be generated on refresh
    if session.has_key('cityFmt'):
        cityFmt = session.get('cityFmt')
        del session['cityFmt']
    else:
        cityFmt = "error"
    if session.has_key('rImg'):
        rImg = session.get('rImg')
        del session['rImg']
    if cityFmt=="error":
        return render_template('correct.html',
            title='Pinpoint',
            refresh=True)
    else:
        return render_template('correct.html',
            title='Pinpoint',
            refresh=False,
            imageUrl=rImg,
            corrMsg=CITIES_DICT[cityFmt])

@application.route('/wrong', methods=['GET'])
def wrong():
    if session.has_key('data'):
        del session['data']
    if session.has_key('idx'):
        del session['idx']
    if session.has_key('allMsg'):
        del session['allMsg']
    if session.has_key('cityFmt'):
        del session['cityFmt']
    # Remove session variables so new ones will be generated on refresh
    if session.has_key('firstCity'):
        firstCity = session.get('firstCity')
        del session['firstCity']
    else:
        firstCity = "error"
    if session.has_key('rImg'):
        rImg = session.get('rImg')
        del session['rImg']
    if firstCity=="error":
        return render_template('wrong.html',
            title='Pinpoint',
            refresh=True)
    else:
        return render_template('wrong.html',
            title='Pinpoint',
            refresh=False,
            imageUrl=rImg,
            corrMsg=CITIES_DICT[firstCity])
