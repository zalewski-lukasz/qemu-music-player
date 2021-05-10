import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from my_auth_module.flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import glob

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['PLAYLIST_PATH'] = 'songs'

users = {
    "root": generate_password_hash("password")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/')
def index():
    all_files = os.listdir(app.config['PLAYLIST_PATH'])
    return render_template('playlist.html', files = all_files)

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def upload_files():
    if request.method == "POST":
       if request.files:
          new_file = request.files['file']
          new_file.save(os.path.join(app.config['PLAYLIST_PATH'], new_file.filename))
    return redirect(url_for('index'))

@app.route('/<filename>')
def download_files(filename):
   return send_from_directory(app.config['PLAYLIST_PATH'], filename, as_attachment=True)

@app.route('/delete/<filename>')
@auth.login_required
def delete_files(filename):
    try:
        os.remove(os.path.join(app.config['PLAYLIST_PATH'], filename))
        return redirect(url_for('index'))
    except Exception as e:
        return "Error!"

if __name__ == '__main__':
    app.run()