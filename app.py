from flask import Flask, render_template_string, request, jsonify
import os
import json
import subprocess
import threading
import webbrowser

app = Flask(__name__)

# Carregar configuração
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "apps_folder": "./apps",
    "port": 5000,
    "title": "🚀 AI Apps Launcher",
    "theme": "dark"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG

config = load_config()
APPS_FOLDER = config.get('apps_folder', './apps')
PORT = config.get('port', 5000)
TITLE = config.get('title', 'AI Apps Launcher')

# Garantir que a pasta existe
os.makedirs(APPS_FOLDER, exist_ok=True)

def get_apps():
    """Lista todos os apps na pasta"""
    apps = []
    if not os.path.exists(APPS_FOLDER):
        return apps
    
    for item in os.listdir(APPS_FOLDER):
        if item.startswith('.'):
            continue
            
        item_path = os.path.join(APPS_FOLDER, item)
        is_dir = os.path.isdir(item_path)
        
        # Detectar ícone e categoria
        if is_dir:
            icon, category = '📁', 'Pasta'
        elif item.endswith(('.bat', '.cmd')):
            icon, category = '⚡', 'Script Windows'
        elif item.endswith('.py'):
            icon, category = '🐍', 'Python'
        elif item.endswith('.exe'):
            icon, category = '💻', 'Executável'
        elif item.endswith('.js'):
            icon, category = '🟨', 'Node.js'
        elif item.endswith('.sh'):
            icon, category = '🐚', 'Shell Script'
        else:
            icon, category = '📄', 'Arquivo'
        
        apps.append({
            'name': item,
            'path': item_path,
            'type': 'folder' if is_dir else 'file',
            'icon': icon,
            'category': category
        })
    
    apps.sort(key=lambda x: x['name'].lower())
    return apps

@app.route('/')
def index():
    apps = get_apps()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{TITLE}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #fff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 20px;
            }}
            h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00d9ff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .subtitle {{ color: #888; font-size: 1.1em; }}
            .stats {{
                display: flex;
                justify-content: center;
                gap: 30px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .stat {{
                background: rgba(255,255,255,0.05);
                padding: 10px 20px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .card {{
                background: rgba(22, 33, 62, 0.8);
                border-radius: 15px;
                padding: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.1);
                position: relative;
                overflow: hidden;
            }}
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0,217,255,0.3);
                border-color: rgba(0,217,255,0.5);
            }}
            .card-icon {{ font-size: 3em; margin-bottom: 15px; }}
            .card-name {{ font-size: 1.3em; font-weight: bold; margin-bottom: 8px; }}
            .card-category {{ color: #00d9ff; font-size: 0.9em; margin-bottom: 10px; }}
            .card-path {{ color: #666; font-size: 0.8em; word-break: break-all; }}
            .btn-launch {{
                display: inline-block;
                margin-top: 15px;
                padding: 10px 20px;
                background: linear-gradient(45deg, #00d9ff, #00ff88);
                color: #1a1a2e;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
            }}
            .refresh-btn {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(45deg, #00d9ff, #00ff88);
                border: none;
                font-size: 1.5em;
                cursor: pointer;
                box-shadow: 0 5px 20px rgba(0,217,255,0.4);
                transition: transform 0.3s;
            }}
            .refresh-btn:hover {{ transform: rotate(180deg); }}
            .empty-state {{
                text-align: center;
                padding: 60px;
                color: #666;
            }}
            .empty-state-icon {{ font-size: 4em; margin-bottom: 20px; }}
            .loading {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.8);
                padding: 20px 40px;
                border-radius: 10px;
                z-index: 1000;
            }}
            .spinner {{
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-top-color: #00d9ff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{TITLE}</h1>
                <p class="subtitle">Gerenciador de Aplicações AI</p>
                <div class="stats">
                    <div class="stat"><strong>{len(apps)}</strong> Apps</div>
                    <div class="stat"><strong>{APPS_FOLDER}</strong> Pasta</div>
                </div>
            </header>
            
            <div class="grid" id="appsGrid">
                {''.join([f"""
                <div class="card" onclick="launchApp('{app['path'].replace('\\\\', '\\\\\\\\').replace("'", "\\'")}')">
                    <div class="card-icon">{app['icon']}</div>
                    <div class="card-name">{app['name']}</div>
                    <div class="card-category">{app['category']}</div>
                    <div class="card-path">{app['path']}</div>
                    <button class="btn-launch">🚀 Abrir</button>
                </div>
                """ for app in apps]) if apps else """
                <div class="empty-state">
                    <div class="empty-state-icon">📂</div>
                    <h2>Nenhum app encontrado</h2>
                    <p>Adicione seus aplicativos na pasta: <strong>./apps</strong></p>
                </div>
                """}
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()" title="Atualizar">🔄</button>
        
        <div class="loading" id="loading">
            <span class="spinner"></span>
            <span>Abrindo...</span>
        </div>
        
        <script>
            function launchApp(path) {{
                document.getElementById('loading').style.display = 'block';
                fetch('/launch', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ path: path }})
                }})
                .then(() => setTimeout(() => {{
                    document.getElementById('loading').style.display = 'none';
                }}, 1000))
                .catch(error => {{
                    console.error('Erro:', error);
                    alert('Erro ao abrir aplicativo');
                    document.getElementById('loading').style.display = 'none';
                }});
            }}
            // Auto-refresh
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    return html

@app.route('/launch', methods=['POST'])
def launch_app():
    try:
        data = request.json
        path = data.get('path', '')
        
        if not path or not os.path.exists(path):
            return jsonify({'error': 'Caminho inválido'}), 400
        
        if os.path.isdir(path):
            subprocess.Popen(['explorer', path])
        elif path.endswith('.py'):
            subprocess.Popen(['cmd', '/k', 'python', path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif path.endswith(('.bat', '.cmd')):
            subprocess.Popen([path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE,
                           cwd=os.path.dirname(path))
        elif path.endswith('.js'):
            subprocess.Popen(['cmd', '/k', 'node', path],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([path])
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps')
def api_apps():
    return jsonify(get_apps())

def open_browser():
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    
    print(f"""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║       🚀  AI APPS LAUNCHER INICIADO!  🚀         ║
    ║                                                   ║
    ║   📂 Pasta: {APPS_FOLDER}
    ║   🌐 URL: http://localhost:{PORT}
    ║   ⚡ Ctrl+C para parar
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)