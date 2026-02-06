import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# جلب المفتاح من إعدادات Railway
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("خطأ: لم يتم العثور على GEMINI_API_KEY في المتغيرات!")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مساعدي الذكي</title>
        <style>
            :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #38bdf8; }
            body { background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: var(--card); padding: 1rem; text-align: center; border-bottom: 1px solid #334155; font-weight: bold; font-size: 1.2rem; }
            #chat-box { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
            .msg { max-width: 85%; padding: 0.8rem 1.2rem; border-radius: 1rem; line-height: 1.6; }
            .user { background: var(--primary); color: #000; align-self: flex-start; border-bottom-right-radius: 0; }
            .ai { background: var(--card); align-self: flex-end; border-bottom-left-radius: 0; border: 1px solid #334155; }
            .input-area { background: var(--card); padding: 1rem; display: flex; gap: 0.5rem; border-top: 1px solid #334155; }
            input { flex: 1; background: #0f172a; border: 1px solid #334155; padding: 0.75rem; border-radius: 999px; color: white; outline: none; }
            button { background: var(--primary); border: none; padding: 0.75rem 1.5rem; border-radius: 999px; color: #000; cursor: pointer; font-weight: bold; }
            .err { color: #ef4444; background: #450a0a; border: 1px solid #ef4444; }
        </style>
    </head>
    <body>
        <header>روبوت الدردشة الخاص بي 🤖</header>
        <div id="chat-box">
            <div class="msg ai">أهلاً بك! أنا جاهز للدردشة. ماذا يدور في ذهنك؟</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="اكتب سؤالك هنا..." onkeypress="if(event.key==='Enter') askAI()">
            <button onclick="askAI()">إرسال</button>
        </div>

        <script>
            async function askAI() {
                const input = document.getElementById('userInput');
                const box = document.getElementById('chat-box');
                const text = input.value.trim();
                if (!text) return;

                appendMsg(text, 'user');
                input.value = '';
                const aiMsg = appendMsg('جاري التفكير...', 'ai');

                try {
                    const res = await fetch(`/chat?user_message=${encodeURIComponent(text)}`);
                    const data = await res.json();
                    if (data.error) {
                        aiMsg.classList.add('err');
                        aiMsg.innerText = "خطأ من جوجل: " + data.error;
                    } else {
                        aiMsg.innerText = data.response;
                    }
                } catch (e) {
                    aiMsg.innerText = "فشل الاتصال بالسيرفر. تأكد من Railway.";
                }
                box.scrollTop = box.scrollHeight;
            }

            function appendMsg(t, c) {
                const d = document.createElement('div');
                d.className = 'msg ' + c;
                d.innerText = t;
                document.getElementById('chat-box').appendChild(d);
                document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
                return d;
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat")
def chat(user_message: str):
    if not API_KEY:
        return {"error": "مفتاح API غير مضبوط في Railway Variables"}
    
    # قائمة الموديلات التي سنحاول تجربتها بالترتيب
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    
    last_error = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"أجب بالعربية: {user_message}")
            return {"response": response.text}
        except Exception as e:
            last_error = str(e)
            continue # تجربة الموديل التالي إذا فشل الحالي
            
    return {"error": f"فشلت جميع النماذج. آخر خطأ: {last_error}"}
