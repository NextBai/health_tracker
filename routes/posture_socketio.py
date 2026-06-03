from flask import session
from models.database import add_posture_record

def register_socketio_events(socketio):
    @socketio.on('posture_update')
    def handle_posture_update(data):
        # 確保在 WebSocket context 下能取得 session
        user_id = session.get('user_id')
        if not user_id:
            return
        add_posture_record(user_id, data)
