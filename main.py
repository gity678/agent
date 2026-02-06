import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()

# إعداد مفتاح Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Llama 3 AI</title>
        <style>
            body { background: #000; color: #00ff00; font-family: 'Courier New', Courier, monospace; display: flex; flex-direction: column; height: 100vh; margin: 0; }
            #chat { flex: 1; overflow-y: auto; padding: 20px; border: 1px solid #00ff00; margin: 10px; border-radius: 10px; }
            .msg { margin-bottom: 15px; padding: 10px; }
            .ai { color: #00ff00; }
            .user { color: #00bfff; }
            .input-box { display: flex; padding: 10px; }
            input { flex: 1; padding: 12px; background: #111; border: 1px solid #00ff00; color: white; border-radius: 5px; }
            button { margin-right: 10px; padding: 10px 20px; background: #00ff00; color: black; border: none; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2 style="text-align:center">Llama 3 AI System 🤖</h2>
        <div id="chat"><div class="msg ai">نظام Llama 3 متصل وجاهز.. اسألني أي شيء.</div></div>
        <div class="input-box">
            <input type="text" id="userInput" placeholder="اكتب أمرك هنا...">
            <button onclick="askAI()">تنفيذ</button>
        </div>
        <script>
            async function askAI() {
                const input = document.getElementById('userInput');
                const chat = document.getElementById('chat');
                const text = input.value;
                if(!text) return;

                append('أنت: ' + text, 'user');
                input.value = '';
                const aiDiv = append('جاري المعالجة...', 'ai');

                try {
                    const res = await fetch(`/chat?user_message=${encodeURIComponent(text)}`);
                    const data = await res.json();
                    aiDiv.innerText = 'Llama 3: ' + (data.response || data.error);
                } catch {
                    aiDiv.innerText = 'خطأ في الاتصال بالسيرفر';
                }
                chat.scrollTop = chat.scrollHeight;
            }
            function append(t, c) {
                const d = document.createElement('div');
                d.className = 'msg ' + c;
                d.innerText = t;
                chat.appendChild(d);
                return d;
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat")
def chat(user_message: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي تجيب باللغة العربية دائماً."},
                {"role": "user", "content": user_message}
            ],
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
