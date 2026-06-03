from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.database import create_user, get_user_by_username
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.html', mode='login')
    
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    user = get_user_by_username(username)
    if user and user['password_hash'] == hash_password(password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth.html', mode='register')
        
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
        
    username = data.get('username')
    password = data.get('password')
    height = float(data.get('height', 0))
    weight = float(data.get('weight', 0))
    age = int(data.get('age', 0))
    gender = data.get('gender', '')
    occupation = data.get('occupation', '')
    
    user_id = create_user(username, hash_password(password), height, weight, age, gender, occupation)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'success': True}), 201
    return jsonify({'error': 'Username already exists'}), 400

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
