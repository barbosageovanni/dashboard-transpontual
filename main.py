#!/usr/bin/env python3
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'transpontual-secret-key-2025'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Transpontual</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
        }
        h1 { color: #fff; text-align: center; margin-bottom: 30px; }
        .status { 
            background: rgba(0,255,0,0.2); 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #00ff00;
        }
        .btn {
            display: inline-block;
            background: #00ff88;
            color: #333;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚂 Dashboard Transpontual</h1>
        <div class="status">
            <h2>✅ Sistema Online!</h2>
            <p><strong>Status:</strong> Funcionando perfeitamente</p>
            <p><strong>Deploy:</strong> Railway</p>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <a href="/login" class="btn">👤 Fazer Login</a>
            <a href="/health" class="btn">🔍 Health Check</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login')
def login():
    return '<h1>🔐 Login</h1><p>admin / Admin123!</p><a href="/">Voltar</a>'

@app.route('/health')
def health():
    import sys
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "dashboard-transpontual",
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}"
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
