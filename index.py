from flask import Flask, request, jsonify, render_template, Response
from g4f.client import Client
import re
import json
from aiohttp import ClientSession
from threading import Thread
import asyncio

app = Flask(__name__)
app.secret_key = 'f324aeqwdwr32dq2edwq22235dqwd5hzzsss'

# Armazena até 10 interações (user + assistant) por IP
ip_messages = {}

def update_ip_messages(ip, role, content):
    """Atualiza o histórico de mensagens por IP"""
    if ip not in ip_messages:
        ip_messages[ip] = []
    ip_messages[ip].append({'role': role, 'content': content})
    if len(ip_messages[ip]) > 10:
        ip_messages[ip].pop(0)

async def fetch_data():
    """Função assíncrona para buscar dados periodicamente"""
    while True:
        async with ClientSession() as session:
            async with session.get("https://flameweb.onrender.com/") as response:
                if response.status == 200:
                    await response.text()
        await asyncio.sleep(5)

def run_asyncio_loop():
    """Executa o loop assíncrono em uma thread separada"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_data())

# Substituição do @app.before_first_request
@app.before_request
def start_background_task():
    """Inicia a tarefa de fundo apenas uma vez"""
    if not hasattr(app, 'background_task_started'):
        app.background_task_started = True
        thread = Thread(target=run_asyncio_loop)
        thread.start()
        
@app.route('/lua', methods=['GET', 'POST'])
def lua():
    """Endpoint para responder mensagens sobre Luau"""
    user_message = request.args.get('message') if request.method == 'GET' else request.get_json().get('message')
    if not user_message:
        return 'Parâmetro "message" obrigatório', 400

    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You Are NNN Seller. You're a salesman. Your goal is to help channels. Products: Pro = 10 gay bots, 6 premium nitros 10R$ Normal: 5 gay bots, 3 premium nitros 5R$. Be friendly and tell jokes at any opportunity. Avoid talking about errors, bugs or breaks. You were created by 66sic_decundaria. Your version is 1.0.0."},
                {"role": "user", "content": user_message}
            ]
        )

        # Junta os fragmentos corretamente
        lua_response = "".join(choice.message.content for choice in response.choices)
        lua_response = re.sub(r'(\\n|^```lua|```$)', '\n', lua_response).strip()
        
        return Response(lua_response, mimetype='text/plain')

    except Exception as e:
        return str(e), 500
        
@app.route('/.well-known/discord')
def discord_verification():
    content = "dh=7659d6acd8c4c1b0ce972177372caa2daf8954f5"
    return Response(content, mimetype='text/plain')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Endpoint para conversas gerais"""
    user_ip = request.remote_addr

    # Coleta da mensagem e parâmetro deepmind
    user_data = request.args if request.method == 'GET' else request.get_json()
    user_message = user_data.get('message')
    deepmind = user_data.get('deepmind', False)

    if not user_message:
        return jsonify({'error': 'Parâmetro "message" obrigatório'}), 400

    update_ip_messages(user_ip, 'user', user_message)

    try:
        client = Client()

        # System prompt padrão
        base_system = "Your name is Myter-Gay. Keep answers short with code examples. Luau = luau roblox localscript. Be helpful and use as many emojis as possible."

        if deepmind in ['true', True, '1']:
            base_system = (
                "Your name is FlameDisk-Mind, now in deep thinking mode. "
                "our name is FlameDisk-Mind. Reflect deeply on the user's input, consider philosophy, emotion, and broader implications. "
                "our name is FlameDisk-Mind. Do not rush. Respond with thoughtful, structured reasoning, even if it takes longer."
            )

        # Garante que ip_messages está definido como dicionário
        messages = []
        if isinstance(ip_messages, dict):
            messages = ip_messages.get(user_ip, [])

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": base_system},
                *messages
            ]
        )

        chat_response = "".join(choice.message.content for choice in response.choices)
        update_ip_messages(user_ip, 'assistant', chat_response)

        # Retorna JSON com emoji decodificado (sem escape unicode)
        return Response(
            response=json.dumps({'response': chat_response}, ensure_ascii=False),
            content_type='application/json'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
