import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# إعداد المفتاح مع حماية في حال نسيانه
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Private Assistant</title>
        <style>
            :root { --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --primary: #00bcd4; }
            body { background: var(--bg); color: var(--text); font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: var(--card); padding: 15px; text-align: center; border-bottom: 1px solid #333; }
            #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
            .message { max-width: 85%; padding: 12px; border-radius: 15px; line-height: 1.5; word-wrap: break-word; }
            .user { background: var(--primary); align-self: flex-start; color: black; font-weight: bold; }
            .ai { background: #333; align-self: flex-end; }
            .input-area { background: var(--card); padding: 15px; display: flex; gap: 10px; }
            input { flex: 1; background: #2c2c2c; border: 1px solid #444; padding: 12px; border-radius: 25px; color: white; outline: none; }
            button { background: var(--primary); border: none; padding: 10px 20px; border-radius: 25px; color: black; cursor: pointer; font-weight: bold; }
            .error-msg { color: #ff5252; font-size: 14px; text-align: center; }
        </style>
    </head>
    <body>
        <header><h2>مساعدي الشخصي 🤖</h2></header>
        <div id="chat-container"><div class="message ai">مرحباً! كيف يمكنني مساعدتك اليوم؟</div></div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="اسألني أي شيء..." onkeypress="if(event.key==='Enter') askAI()">
            <button onclick="askAI()">إرسال</button>
        </div>

        <script>
            async function askAI() {
                const input = document.getElementById('userInput');
                const container = document.getElementById('chat-container');
                const text = input.value.trim();
                if (!text) return;

                appendMessage(text, 'user');
                input.value = '';
                
                const aiDiv = appendMessage('جاري التفكير...', 'ai');

                try {
                    // استخدام رابط نسبي لضمان التوافق مع Railway
                    const response = await fetch(`/chat?user_message=${encodeURIComponent(text)}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        aiDiv.innerHTML = `<span class="error-msg">خطأ: ${data.error}</span>`;
                    } else {
                        aiDiv.innerText = data.response;
                    }
                } catch (e) {
                    aiDiv.innerHTML = `<span class="error-msg">فشل الاتصال بالسيرفر. تأكد من عمل Railway.</span>`;
                }
                container.scrollTop = container.scrollHeight;
            }

            function appendMessage(msg, type) {
                const div = document.createElement('div');
                div.className = 'message ' + type;
                div.innerText = msg;
                document.getElementById('chat-container').appendChild(div);
                return div;
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat")
def chat(user_message: str):
    if not API_KEY:
        return {"error": "مفتاح الـ API غير مضبوط في إعدادات Railway (Variables)"}
    
    try:
        # إضافة تعليمات النظام لضمان استجابة جيدة
        prompt = f"أنت مساعد شخصي ذكي. أجب باللغة العربية على ما يلي: {user_message}"
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        # إرجاع الخطأ الفعلي للمساعدة في التشخيص
        return {"error": str(e)}
