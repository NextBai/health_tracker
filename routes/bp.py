from flask import Blueprint, request, jsonify, session
from models.database import add_bp_record, get_recent_bps

bp_bp = Blueprint('bp', __name__)

@bp_bp.route('/api/bp', methods=['GET', 'POST'])
def manage_bp():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
            
        systolic = int(data.get('systolic', 0))
        diastolic = int(data.get('diastolic', 0))
        heart_rate = int(data.get('heart_rate', 0))
        
        if systolic > 0 and diastolic > 0 and heart_rate > 0:
            add_bp_record(user_id, systolic, diastolic, heart_rate)
            return jsonify({'success': True}), 201
        return jsonify({'error': 'Invalid data'}), 400
        
    elif request.method == 'GET':
        records = get_recent_bps(user_id)
        return jsonify(records), 200
