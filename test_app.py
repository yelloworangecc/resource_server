import pytest
from app import app
from pathlib import Path
import os,time

app.config["TESTING"] = True
app.config["IMAGE_DIR"] = str( Path(__file__).parent / 'test' / 'images')
app.config["VIDEO_DIR"] = str( Path(__file__).parent / 'test' / 'videos')

client = app.test_client()
runner = app.test_cli_runner()

token = app.config['FERNET'].encrypt(os.getenv("SECRET_KEY").encode()).decode("UTF-8")

def test_request_favicon():
    response = client.get('/favicon.ico')
    assert response.content_type == 'image/vnd.microsoft.icon'

def test_image_index():
    response = client.get('/images/')
    assert response.data == b'<h1>Hello Blueprint Image!</h1>'
    
def test_post_image():
    check_image = Path(app.config["IMAGE_DIR"]) / 'test' / 'profile.jpg'
    if check_image.exists():
        os.remove(str(check_image))
    post_image = Path(__file__).parent / 'test' / 'profile.jpg'
    response = client.post('/images/test?token={0}'.format(token), data={'file':post_image.open('rb')})
    assert check_image.exists()

def test_get_ablums():
    response = client.get('/images/get_ablums')
    json_data = response.get_json()
    assert 'test' in json_data

def test_get_images():
    response = client.get('/images/get_images?ablum=test')
    json_data = response.get_json()
    assert 'profile.jpg' in json_data
    
def test_get_image():
    response = client.get('/images/test/profile.jpg')
    assert response.content_type == 'image/jpeg'

def test_video_index():
    response = client.get('/videos/')
    assert response.data == b'<h1>Hello Blueprint Video!</h1>'

def test_post_video():
    check_video = Path(app.config["VIDEO_DIR"]) / 'test' / '01' / '01.mp4'
    check_playlist = Path(app.config["VIDEO_DIR"]) / 'test' / '01' / 'playlist.m3u8'
    if check_video.exists():
        os.remove(str(check_video))
    if check_playlist.exists():
        os.remove(str(check_playlist))
    
    post_video = Path(__file__).parent / 'test' / '01.mp4'
    response = client.post('/videos/test?token={0}'.format(token), data={'file':post_video.open('rb')})
    time.sleep(5)
    assert check_playlist.exists()

def test_get_serials():
    response = client.get('/videos/get_serials')
    json_data = response.get_json()
    assert 'test' in json_data

def test_get_episodes():
    response = client.get('/videos/get_episodes?serial=test')
    json_data = response.get_json()
    assert '01' in json_data

def test_get_video():
    response = client.get('/videos/test/01/playlist.m3u8')
    assert response.content_type = 'application/vnd.apple.mpegurl'
