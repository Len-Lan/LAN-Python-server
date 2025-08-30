import json
import os
import time
from functools import wraps
from flask import Flask, request, redirect, url_for, session, jsonify
from flask_cors import CORS  # 添加CORS支持

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'  # 使用更强的密钥

# 添加CORS支持，允许跨域请求
CORS(app, supports_credentials=True)

# 用户数据文件路径
USERS_FILE = 'users.json'
# 访问记录文件路径
ACCESS_LOG_FILE = 'access_log.json'

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """保存用户数据"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def log_access(username, action, filename=None):
    """记录用户访问行为"""
    access_log = load_access_log()
    log_entry = {
        'timestamp': time.time(),
        'time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
        'username': username,
        'action': action,
        'filename': filename,
        'ip': request.remote_addr
    }
    
    # 将新记录添加到日志开头
    access_log.insert(0, log_entry)
    
    # 只保留最近1000条记录
    if len(access_log) > 1000:
        access_log = access_log[:1000]
    
    save_access_log(access_log)

def load_access_log():
    """加载访问记录"""
    if os.path.exists(ACCESS_LOG_FILE):
        with open(ACCESS_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_access_log(access_log):
    """保存访问记录"""
    with open(ACCESS_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(access_log, f, indent=4, ensure_ascii=False)

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """处理登录请求"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    users = load_users()
    
    # 检查用户是否存在且密码正确
    if username in users and users[username]['password'] == password:
        session['username'] = username
        # 记录登录成功
        log_access(username, 'login_success')
        response = jsonify({'success': True, 'message': '登录成功'})
        return _corsify_actual_response(response)
    else:
        # 记录登录失败
        log_access(username, 'login_failed')
        response = jsonify({'success': False, 'message': '用户名或密码错误'})
        return _corsify_actual_response(response)

@app.route('/logout', methods=['GET', 'OPTIONS'])
def logout():
    """处理退出登录"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'username' in session:
        username = session['username']
        log_access(username, 'logout')
    
    session.pop('username', None)
    response = jsonify({'success': True, 'message': '已退出登录'})
    return _corsify_actual_response(response)

@app.route('/check_auth', methods=['GET', 'OPTIONS'])
def check_auth():
    """检查认证状态"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'username' in session:
        response = jsonify({'authenticated': True, 'username': session['username']})
    else:
        response = jsonify({'authenticated': False})
    return _corsify_actual_response(response)

@app.route('/access_logs', methods=['GET', 'OPTIONS'])
def get_access_logs():
    """获取访问记录"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # 检查用户是否已登录
    if 'username' not in session:
        response = jsonify({'success': False, 'message': '未登录'})
        return _corsify_actual_response(response)
    
    # 只允许管理员查看访问记录
    users = load_users()
    username = session['username']
    if username in users and users[username].get('role') == 'admin':
        logs = load_access_log()
        # 限制返回最近50条记录
        response = jsonify({'success': True, 'logs': logs[:50]})
    else:
        response = jsonify({'success': False, 'message': '权限不足'})
    
    return _corsify_actual_response(response)

def _build_cors_preflight_response():
    """处理预检请求"""
    response = jsonify()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

def _corsify_actual_response(response):
    """添加CORS头到实际响应"""
    response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == '__main__':
    # 修改为在所有网络接口上运行，而不仅仅是本地
    app.run(debug=True, host='0.0.0.0', port=5000)