import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# إعداد المفتاح
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    # تهيئة المكتبة
    genai.configure(api_key=API_KEY)
else:
    print("المفتاح مفقود!")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Bot</title>
        <style>
            body { background: #111; color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
            #chat { flex: 1; overflow-y: auto; padding: 20px; }
            .msg { margin-bottom: 15px; padding: 10px; border-radius: 10px; max-width: 80%; }
            .ai { background: #333; align-self: flex-end; }
            .user { background: #007bff; align-self: flex-start; }
            .input-box { display: flex; padding: 10px; background: #222; }
            input { flex: 1; padding: 10px; border: none; border-radius: 5px; }
            button { margin-right: 10px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div id="chat"><div class="msg ai">أهلاً بك.. جرب الآن بعد التحديث.</div></div>
        <div class="input-box">
            <input type="text" id="userInput" placeholder="اكتب هنا...">
            <button onclick="askAI()">إرسال</button>
        </div>
        <script>
            async function askAI() {
                const input = document.getElementById('userInput');
                const chat = document.getElementById('chat');
                const text = input.value;
                if(!text) return;

                const userDiv = document.createElement('div');
                userDiv.className = 'msg user';
                userDiv.innerText = text;
                chat.appendChild(userDiv);
                input.value = '';

                const aiDiv = document.createElement('div');
                aiDiv.className = 'msg ai';
                aiDiv.innerText = 'جاري الرد...';
                chat.appendChild(aiDiv);

                try {
                    const res = await fetch(`/chat?user_message=${encodeURIComponent(text)}`);
                    const data = await res.json();
                    aiDiv.innerText = data.response || data.error;
                } catch {
                    aiDiv.innerText = 'خطأ في الاتصال';
                }
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat")
def chat(user_message: str):
    if not API_KEY:
        return {"error": "تأكد من وضع المفتاح في Railway Variables باسم GEMINI_API_KEY"}
    
    try:
        # استخدام الموديل بالاسم المختصر الصريح
        model = genai.GenerativeModel('gemini-1.5-flash')
        # طلب الرد
        response = model.generate_content(user_message)
        return {"response": response.text}
    except Exception as e:
        return {"error": f"جوجل تقول: {str(e)}"}
