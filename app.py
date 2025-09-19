from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from downloader import *
import re
from datetime import timedelta


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for sessions

app.permanent_session_lifetime = timedelta(hours=3)

@app.before_request
def make_session_temporary():
    session.permanent = False  # <-- set per-request, not globally

@app.route('/', methods=['GET', 'POST'])
def video_download():
    context = {
    'url': session.get('url', ''),
    'choice': session.get('choices', ''),
    'info': session.get('info', {'title':'', 'size':'', 'res_size':{}})
    }
    
    if request.method == "POST":
        if 'search' in request.form or 'search.x' in request.form:
            context['url'] = request.form.get('url') # Get URL
            context['choice'] = request.form.get('choice') # Get ext
            if context['choice'] == "mp3":
                try:
                    context['info']['title'], context['info']['size'] = info_mp3(context['url'])
                except UnboundLocalError:
                    context["error"] = "Invaild Link!"
                    session.clear()

            if context['choice'] == "mp4":
                try:
                    context['info']['title'], context['info']['res_size'] = info_mp4(context['url'])
                except UnboundLocalError:
                    context["error"] = "Invaild Link!"
                    session.clear()

            # Save in session
            session['url'] = context['url']
            session['choice'] = context['choice']
            session['info'] = context['info']

        elif 'downloadmp3' in request.form:
            progress_data["progress"] = 0
            progress_data["cancel"] = False
            download_mp3(context['url'], context['info']['title'])
            session.clear()
            return redirect(url_for('video_download'))
        
        else:
            for key in request.form.keys():
                if key.startswith("download"):
                    progress_data["progress"] = 0
                    progress_data["cancel"] = False
                    clicked = key
                    height = re.search(r'\d+', clicked).group()
                    download_mp4(context['url'], height, context['info']['title'])
                    break
            session.clear()
            return redirect(url_for('video_download'))

        return render_template('base.html', **context)
    
    return render_template('base.html', **context) # GET (At the first when open route before entering data)


@app.route("/progress")
def progress():
    return jsonify(progress_data)

@app.route("/cancel", methods=["POST"])
def cancel():
    cancel_download()
    return jsonify({"status": "canceled"})