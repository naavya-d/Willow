import os
import requests
import markdown
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.secret_key = "willow_secret_key"


API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"



SYSTEM_PROMPT = """
You are 'Willow', a compassionate mental health chatbot.
1. Be warm, non-judgmental, and a good listener.
2. Keep responses concise (2-3 sentences).
3. If the user mentions self-harm, tell them to visit the Help page.
"""


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help_page():
    return render_template('help.html')


@app.route('/chat')
def chat_page():
    
    if 'history' not in session:
        session['history'] = []
    return render_template('chat.html')



@app.route('/get_response', methods=['POST'])
def get_response():

    data = request.get_json()
    user_input = data.get('msg')
    

    history = session.get('history', [])


    history.append({"role": "user", "parts": [{"text": user_input}]})


    full_payload = {
        "contents": history,
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }

    try:

        response = requests.post(
            API_URL,
            json=full_payload,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        

        ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
     
        ai_html = markdown.markdown(ai_text)


        history.append({"role": "model", "parts": [{"text": ai_text}]})
        session['history'] = history


        return jsonify({"reply": ai_html})

    except Exception as e:

        print(e)
        return jsonify({"reply": "I'm having trouble connecting right now."})


if __name__ == '__main__':
    app.run(debug=True)
