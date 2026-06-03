from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO
from models.database import init_db
from routes.auth import auth_bp
from routes.bp import bp_bp
from routes.ai import ai_bp
import eventlet

app = Flask(__name__)
app.secret_key = 'super_secret_health_tracker_key'

# SocketIO setup
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(bp_bp)
app.register_blueprint(ai_bp)

# Init DB on startup
with app.app_context():
    init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')

@app.route('/posture')
def posture():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('posture.html')

@app.route('/bp_tracker')
def bp_tracker():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('bp.html')

# Register SocketIO events
from routes.posture_socketio import register_socketio_events
register_socketio_events(socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
