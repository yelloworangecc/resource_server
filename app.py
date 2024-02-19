import os
from cryptography.fernet import Fernet
from flask import Flask
from flask import send_from_directory
from blueprints import bp_video
from blueprints import bp_image
from pathlib import Path

# initialize app
app = Flask(__name__)
app.app_context().push()
app.secret_key = os.getenv('SECRET_KEY') # must
app.config['FERNET'] = Fernet(os.getenv("FERNET_KEY").encode())
app.config["IMAGE_DIR"] = os.getenv('RESOURCE_IMAGES')
app.config["VIDEO_DIR"] = os.getenv('RESOURCE_VIDEOS')
if not app.config["IMAGE_DIR"]:
    app.config["IMAGE_DIR"] = str( Path(__file__).parent / 'blueprints' / 'images' )
if not app.config["VIDEO_DIR"]:
    app.config["VIDEO_DIR"] = str( Path(__file__).parent / 'blueprints' / 'videos' )

# register the top level blue print
app.register_blueprint(bp_video)
app.register_blueprint(bp_image)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# run debug mode
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
