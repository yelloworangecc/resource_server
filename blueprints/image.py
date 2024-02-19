from flask import Blueprint
from flask import send_file
from flask import request
from flask import abort
from flask import jsonify
from flask import current_app

import os,time

prefix = "/images"
bp_image = Blueprint('image', __name__, url_prefix=prefix)
request_ttl = 360 # 6minutes

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

@bp_image.route('/')
def root():
    return "<h1>Hello Blueprint Image!</h1>"

@bp_image.route('/index')
def index():
    return "<h1>Hello Blueprint Image!</h1>"

@bp_image.route('/index.html')
def index_html():
    return "<h1>Hello Blueprint Image!</h1>"

# curl http://127.0.0.1:5000/images/get_ablums
# [
#   "private",
#   "test"
# ]
@bp_image.route('/get_ablums')
def get_ablums():
    ablum_list = []
    for item in os.scandir(current_app.config["IMAGE_DIR"]):
        if item.is_dir():
            ablum_list.append(item.name)
    return jsonify(ablum_list)

# curl http://127.0.0.1:5000/images/get_images?ablum=test
# curl http://127.0.0.1:5000/images/get_images?ablum=test&token=x
# [
#   "profile.jpg"
# ]
@bp_image.route('/get_images')
def get_images():
    if "ablum" not in request.args:
        return "argument ablum is required"
    ablum = request.args["ablum"]
    if ablum == "private" and not check_fernet():
        return abort(403)
    
    image_list = []
    ablum_path = os.path.join(current_app.config["IMAGE_DIR"],ablum)
    for item in os.scandir(ablum_path):
        if item.is_file():
            image_list.append(item.name)
    return jsonify(image_list)

# curl http://127.0.0.1:5000/images/test/profile.jpg
# curl -X DELETE http://127.0.0.1:5000/images/test/profile1706851849.jpg?token=x
@bp_image.route('/<ablum>/<name>', methods=['GET','DELETE'])
def get_image(ablum,name):
    if (ablum == "private" or request.method == 'DELETE') and not check_fernet():
        return abort(403)

    image_path = os.path.join(current_app.config["IMAGE_DIR"],ablum,name)

    if os.path.exists(image_path):
        if request.method == 'GET':
            return send_file(image_path)
        else:
            os.remove(image_path)
            return 'OK'
    else:
        return abort(404)

# curl -F file=@profile.jpg http://127.0.0.1:5000/images/test?token=x
@bp_image.route('/<ablum>', methods=['POST'])
def post_image(ablum):
    if not check_fernet():
        return abort(403)

    ablum_path = os.path.join(current_app.config["IMAGE_DIR"],ablum)
    if not os.path.exists(ablum_path):
        os.mkdir(ablum_path)

    if 'file' not in request.files or not request.files['file']:
        return "file not in the request"
    posted_file = request.files['file']
    if not posted_file or not posted_file.filename:
        return "no file found"

    name_split_list = posted_file.filename.rsplit('.', 1)
    posted_filetype = name_split_list[1].lower()
    if posted_filetype in ['jpg','jpeg','png','gif','bmp']:
        image_path = os.path.join(ablum_path, os.path.basename(posted_file.filename))
        
        # image path exist, add timestamp to image name
        if os.path.exists(image_path):
            image_path = os.path.join(ablum_path, name_split_list[0]+str(int(time.time()))+'.'+posted_filetype)
        posted_file.save(image_path)
        return "OK"
    else:
        return "file type error"
            
