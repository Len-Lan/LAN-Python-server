import os
import sys
import socket
import json

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个临时连接来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 连接到一个公共DNS服务器
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # 失败时返回回环地址

def get_file_size(file_path):
    """获取文件大小并转换为易读格式"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def get_file_icon(filename):
    """根据文件扩展名返回对应的图标类"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
        return 'fas fa-file-video', '视频文件'
    elif ext in ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.php', '.rb', '.go']:
        return 'fas fa-file-code', '代码文件'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
        return 'fas fa-file-image', '图片文件'
    elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
        return 'fas fa-file-alt', '文档文件'
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return 'fas fa-file-archive', '压缩文件'
    else:
        return 'fas fa-file', '其他文件'

def generate_index(directory):
    # 获取本机IP
    local_ip = get_local_ip()
    print(f"检测到本机IP: {local_ip}")
    
    # 需要隐藏的文件列表（登录相关文件）
    hidden_files = [
        'auth.py', 
        'users.json', 
        'config.py', 
        'requirements.txt',
        'generate_index.py',
        'generate_index.py.bak',
        '.htaccess',
        'access_log.json'  # 添加访问记录文件到隐藏列表
    ]
    
    # 获取目录中的所有文件（排除隐藏文件、index.html本身和指定文件）
    files = [f for f in os.listdir(directory) 
             if os.path.isfile(os.path.join(directory, f)) and 
             not f.startswith('.') and 
             f != 'index.html' and
             f not in hidden_files]
    
    # 统计文件类型
    file_types = {}
    for file in files:
        _, ext = os.path.splitext(file)
        ext = ext.lower()
        file_types[ext] = file_types.get(ext, 0) + 1
    
    # 生成HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件共享服务器</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-color: #1a2980;
            --secondary-color: #26d0ce;
            --accent-color: #ff7e5f;
            --light-color: #ffffff;
            --dark-color: #2c3e50;
            --success-color: #38ef7d;
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            --transition: all 0.3s ease;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: var(--light-color);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
            background-attachment: fixed;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
        }}
        
        h1 {{
            font-size: 2.8rem;
            color: white;
            margin-bottom: 10px;
            font-weight: 700;
            position: relative;
            display: inline-block;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }}
        
        h1:after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 4px;
            background: var(--accent-color);
            border-radius: 2px;
        }}
        
        .subtitle {{
            color: rgba(255, 255, 255, 0.85);
            font-size: 1.2rem;
            margin-top: 20px;
        }}
        
        .search-box {{
            max-width: 500px;
            margin: 30px auto;
            position: relative;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 50px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            font-size: 1rem;
            transition: var(--transition);
            background: rgba(255, 255, 255, 0.9);
        }}
        
        .search-box input:focus {{
            outline: none;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
            background: white;
        }}
        
        .search-box i {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--primary-color);
        }}
        
        .file-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }}
        
        .file-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--card-shadow);
            transition: var(--transition);
            display: flex;
            flex-direction: column;
            height: 100%;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .file-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
        }}
        
        .file-card-header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 15px;
            text-align: center;
        }}
        
        .file-card-header i {{
            font-size: 2.2rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        
        .file-card-body {{
            padding: 20px;
            flex-grow: 1;
        }}
        
        .file-name {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: var(--dark-color);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .file-meta {{
            display: flex;
            justify-content: space-between;
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        
        .file-card-footer {{
            padding: 0 20px 20px;
        }}
        
        .download-btn {{
            display: block;
            width: 100%;
            padding: 12px;
            background: var(--success-color);
            color: white;
            text-align: center;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: var(--transition);
            box-shadow: 0 4px 10px rgba(56, 239, 125, 0.4);
        }}
        
        .download-btn:hover {{
            background: #2dd56a;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(56, 239, 125, 0.5);
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.2rem;
            font-weight: 700;
            color: white;
            text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        
        .stat-label {{
            color: rgba(255, 255, 255, 0.85);
            font-size: 0.9rem;
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .file-grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 2.2rem;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 20px;
            }}
        }}
        
        /* 登录相关样式 */
        .login-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            padding: 40px;
            width: 100%;
            max-width: 400px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
        }}
        
        .login-header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .login-header h1 {{
            font-size: 2rem;
            color: var(--primary-color);
            margin-bottom: 10px;
        }}
        
        .login-header p {{
            color: #6c757d;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: var(--dark-color);
            font-weight: 600;
        }}
        
        .form-group input {{
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
            transition: var(--transition);
        }}
        
        .form-group input:focus {{
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(26, 41, 128, 0.1);
        }}
        
        .login-btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .login-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .file-container {{
            display: none;
        }}
        
        /* 访问记录表格样式 */
        .access-logs {{
            margin: 30px 0;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .access-logs h2 {{
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        
        .access-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .access-table th,
        .access-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        .access-table th {{
            background-color: var(--primary-color);
            color: white;
            font-weight: 600;
        }}
        
        .access-table tr:hover {{
            background-color: rgba(26, 41, 128, 0.05);
        }}
        
        .access-table-container {{
            max-height: 400px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div class="login-container" id="loginContainer">
        <div class="login-header">
            <h1>文件共享平台</h1>
            <p>请输入凭证访问文件</p>
        </div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" placeholder="请输入用户名" required>
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="login-btn">登录</button>
        </form>
        <div id="loginMessage" style="color: red; margin-top: 15px; text-align: center;"></div>
    </div>

    <div class="file-container" id="fileContainer">
        <div class="container">
            <header>
                <h1>文件共享中心</h1>
                <p class="subtitle">安全、便捷的文件共享平台</p>
                
                <div style="display: flex; justify-content: space-between; align-items: center; max-width: 500px; margin: 0 auto;">
                    <div class="search-box">
                        <input type="text" placeholder="搜索文件...">
                        <i class="fas fa-search"></i>
                    </div>
                    <div style="color: white; margin-left: 20px;">
                        欢迎, <span id="userName">用户</span> | 
                        <a href="#" onclick="logout()" style="color: white; text-decoration: underline;">退出</a>
                    </div>
                </div>
            </header>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(files)}</div>
                    <div class="stat-label">总文件数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{sum(1 for f in files if os.path.splitext(f)[1].lower() in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'])}</div>
                    <div class="stat-label">视频文件</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{sum(1 for f in files if os.path.splitext(f)[1].lower() in ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.php', '.rb', '.go'])}</div>
                    <div class="stat-label">代码文件</div>
                </div>
            </div>
            
            <!-- 访问记录区域 -->
            <div class="access-logs" id="accessLogs" style="display: none;">
                <h2>最近访问记录</h2>
                <div class="access-table-container">
                    <table class="access-table">
                        <thead>
                            <tr>
                                <th>时间</th>
                                <th>用户</th>
                                <th>操作</th>
                                <th>文件名</th>
                                <th>IP地址</th>
                            </tr>
                        </thead>
                        <tbody id="accessLogsBody">
                            <!-- 访问记录将通过JavaScript动态填充 -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="file-grid">
'''
    
    # 为每个文件添加卡片
    for file in files:
        file_path = os.path.join(directory, file)
        icon_class, file_type = get_file_icon(file)
        file_size = get_file_size(file_path)
        file_ext = os.path.splitext(file)[1].upper().replace('.', '') or '文件'
        
        html_content += f'''
                <div class="file-card">
                    <div class="file-card-header">
                        <i class="{icon_class}"></i>
                        <div>{file_type}</div>
                    </div>
                    <div class="file-card-body">
                        <div class="file-name">{file}</div>
                        <div class="file-meta">
                            <span>{file_ext}</span>
                            <span>{file_size}</span>
                        </div>
                    </div>
                    <div class="file-card-footer">
                        <a href="{file}" class="download-btn" data-filename="{file}">查看</a>
                    </div>
                </div>
'''
    
    # 闭合HTML标签
    html_content += f'''
            </div>
            
            <footer>
                <p>© 101 文件共享服务器 | 已共享 {len(files)} 个文件</p>
            </footer>
        </div>
    </div>

    <script>
        // 检查认证状态
        function checkAuth() {{
            fetch('http://{local_ip}:5000/check_auth', {{
                method: 'GET',
                credentials: 'include'  // 确保发送cookie
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('网络响应不正常');
                }}
                return response.json();
            }})
            .then(data => {{
                if (data.authenticated) {{
                    document.getElementById('loginContainer').style.display = 'none';
                    document.getElementById('fileContainer').style.display = 'block';
                    document.getElementById('userName').textContent = data.username;
                    
                    // 设置下载链接的事件监听器
                    setupDownloadLinks();
                    
                    // 如果是管理员，获取访问记录
                    if (data.username === 'admin') {{
                        fetchAccessLogs();
                    }}
                }} else {{
                    document.getElementById('loginContainer').style.display = 'block';
                    document.getElementById('fileContainer').style.display = 'none';
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                document.getElementById('loginMessage').textContent = '无法连接到认证服务，请确保认证服务已启动';
            }});
        }}
        
        // 处理登录表单提交
        document.getElementById('loginForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const messageEl = document.getElementById('loginMessage');
            
            // 发送登录请求
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            
            fetch('http://{local_ip}:5000/login', {{
                method: 'POST',
                body: formData,
                credentials: 'include'  // 确保发送cookie
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('网络响应不正常');
                }}
                return response.json();
            }})
            .then(data => {{
                if (data.success) {{
                    messageEl.textContent = '';
                    checkAuth(); // 重新检查认证状态
                }} else {{
                    messageEl.textContent = data.message;
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                messageEl.textContent = '登录请求失败，请确保认证服务已启动';
            }});
        }});
        
        // 退出登录
        function logout() {{
            fetch('http://{local_ip}:5000/logout', {{
                method: 'GET',
                credentials: 'include'  // 确保发送cookie
            }})
            .then(() => {{
                checkAuth(); // 重新检查认证状态
            }})
            .catch(error => {{
                console.error('Error:', error);
            }});
        }}
        
        // 文件搜索功能
        document.querySelector('.search-box input').addEventListener('keyup', function() {{
            const searchText = this.value.toLowerCase();
            const fileCards = document.querySelectorAll('.file-card');
            
            fileCards.forEach(card => {{
                const fileName = card.querySelector('.file-name').textContent.toLowerCase();
                if (fileName.includes(searchText)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }});
        
        // 获取访问记录
        function fetchAccessLogs() {{
            fetch('http://{local_ip}:5000/access_logs', {{
                method: 'GET',
                credentials: 'include'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    displayAccessLogs(data.logs);
                }} else {{
                    console.log('无法获取访问记录:', data.message);
                }}
            }})
            .catch(error => {{
                console.error('获取访问记录错误:', error);
            }});
        }}

        // 显示访问记录
        function displayAccessLogs(logs) {{
            const logsBody = document.getElementById('accessLogsBody');
            logsBody.innerHTML = '';
            
            if (logs.length === 0) {{
                logsBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无访问记录</td></tr>';
                return;
            }}
            
            logs.forEach(log => {{
                const row = document.createElement('tr');
                
                const timeCell = document.createElement('td');
                timeCell.textContent = log.time_str || new Date(log.timestamp * 1000).toLocaleString();
                
                const userCell = document.createElement('td');
                userCell.textContent = log.username || '未知用户';
                
                const actionCell = document.createElement('td');
                let actionText = log.action;
                if (log.action === 'login_success') actionText = '登录成功';
                else if (log.action === 'login_failed') actionText = '登录失败';
                else if (log.action === 'logout') actionText = '退出登录';
                else if (log.action === 'file_access') actionText = '访问文件';
                actionCell.textContent = actionText;
                
                const fileCell = document.createElement('td');
                fileCell.textContent = log.filename || '-';
                
                const ipCell = document.createElement('td');
                ipCell.textContent = log.ip || '未知IP';
                
                row.appendChild(timeCell);
                row.appendChild(userCell);
                row.appendChild(actionCell);
                row.appendChild(fileCell);
                row.appendChild(ipCell);
                
                logsBody.appendChild(row);
            }});
            
            // 显示访问记录区域
            document.getElementById('accessLogs').style.display = 'block';
        }}
        
        // 为所有下载链接添加点击事件监听器
        function setupDownloadLinks() {{
            document.querySelectorAll('.download-btn').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    const filename = this.getAttribute('data-filename');
                    
                    // 记录文件访问
                    fetch('http://{local_ip}:5000/log_file_access', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }},
                        body: 'filename=' + encodeURIComponent(filename),
                        credentials: 'include'
                    }}).catch(error => {{
                        console.error('记录文件访问错误:', error);
                    }});
                    
                    // 允许默认行为（下载文件）
                }});
            }});
        }}
        
        // 页面加载时检查认证状态
        document.addEventListener('DOMContentLoaded', checkAuth);
    </script>
</body>
</html>'''
    
    # 写入index.html文件
    with open(os.path.join(directory, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"已生成美化索引页面，包含 {len(files)} 个文件")
    print(f"已隐藏以下文件: {', '.join(hidden_files)}")
    print(f"认证服务地址: http://{local_ip}:5000")
    print("请确保认证服务已启动: python auth.py")

if __name__ == "__main__":
    # 如果没有指定目录，使用当前目录
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_index(directory)