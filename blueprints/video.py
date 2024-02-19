from flask import Blueprint
from flask import send_file
from flask import request
from flask import abort
from flask import jsonify
from flask import current_app
from flask import render_template

import os,time

prefix = "/videos"
bp_video = Blueprint('video', __name__, url_prefix=prefix)
request_ttl = 3600 # 1hour

def check_fernet():
    try:
        token=request.args["token"].encode()
        if current_app.debug or current_app.testing:
            request_ttl = 86400 # 1day
        key = current_app.config['FERNET'].decrypt(token,ttl=request_ttl)
        if current_app.secret_key.encode() == key:
            return True
        else:
            return False
    except:
        return False

@bp_video.route('/')
def root():
    return "<h1>Hello Blueprint Video!</h1>"

@bp_video.route('/index')
def index():
    return "<h1>Hello Blueprint Video!</h1>"

@bp_video.route('/index.html')
def index_html():
    return "<h1>Hello Blueprint Video!</h1>"

@bp_video.route('/get_serials')
def get_serials():
    serial_list = []
    for item in os.scandir(current_app.config["VIDEO_DIR"]):
        if item.is_dir():
            serial_list.append(item.name)
    return jsonify(serial_list)

@bp_video.route('/get_episodes')
def get_episodes():
    if "serial" not in request.args:
        return "argument serial is required"
    serial = request.args["serial"]
    if serial == "private" and not check_fernet():
        return abort(403)
    
    episode_list = []
    serial_dir = os.path.join(current_app.config["VIDEO_DIR"],serial)
    for item in os.scandir(serial_dir):
        if item.is_dir():
            episode_list.append(item.name)
    return jsonify(episode_list)

# curl http://127.0.0.1:5000/videos/LinearAlgebra/01/playlist.m3u8
@bp_video.route('/<serial>/<episode>/<name>')
def get_video(serial,episode,name):
    target_filetype = name.rsplit('.', 1)[1].lower()
    if serial == "private" and target_filetype == 'm3u8' and not check_fernet():
        return abort(403)

    if target_filetype not in ['m3u8','ts']:
        return abort(404)
    
    file_path = os.path.join(current_app.config["VIDEO_DIR"],serial,episode,name)
    if not os.path.exists(file_path):
        return abort(404)

    return send_file(file_path)

# curl -F file=@01.mp4 http://127.0.0.1:5000/videos/LinearAlgebra?token=x
@bp_video.route('/<serial>', methods=['POST'])
def post_video(serial):
    if not check_fernet():
        return abort(403)

    serial_dir = os.path.join(current_app.config["VIDEO_DIR"],serial)
    if not os.path.exists(serial_dir):
        os.mkdir(serial_dir)

    posted_file = request.files['file']
    if not posted_file or not posted_file.filename:
        return "no file found"

    name_split_list = os.path.basename(posted_file.filename).rsplit('.', 1)
    posted_filetype = name_split_list[1].lower()
    if posted_filetype in ['mp4','mov','wmv','flv','avi','mkv']:
        episode_dir = os.path.join(serial_dir,name_split_list[0])
        if not os.path.exists(episode_dir):
            os.mkdir(episode_dir)

        video_path = os.path.join(episode_dir, os.path.basename(posted_file.filename))
        if os.path.exists(video_path):
            return "episode video " + posted_file.filename + " already exists"

        posted_file.save(video_path)
        os.system('ffmpeg -i {0} -vcodec copy -acodec copy -f segment -segment_list {1}/playlist.m3u8 -segment_time 10 {1}/%d.ts'.format(video_path,episode_dir))
        time.sleep(2)
        return 'OK'
    else:
        return "file type error"

# chrome http://127.0.0.1:5000/videos/LinearAlgebra/01
@bp_video.route('/<serial>/<episode>')
def play_video(serial,episode):
    return render_template('video_play.html',serial=serial,episode=episode)
