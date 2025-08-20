from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚂 Dashboard Transpontual</h1>
    <h2>✅ Sistema Online - Railway!</h2>
    <p><a href="/login">👉 Login</a></p>
    <p>Status: Funcionando</p>
    '''

@app.route('/login')
def login():
    return '<h1>Login em desenvolvimento</h1><a href="/">Voltar</a>'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
