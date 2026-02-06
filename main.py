from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os

app = FastAPI()

# إعداد الذكاء الاصطناعي باستخدام المفتاح الذي وضعته في Railway
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

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
            :root { --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --primary: #3f51b5; }
            body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: var(--card); padding: 15px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
            #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
            .message { max-width: 80%; padding: 12px; border-radius: 15px; line-height: 1.5; font-size: 16px; }
            .user { background: var(--primary); align-self: flex-start; color: white; }
            .ai { background: var(--card); align-self: flex-end; border: 1px solid #333; }
            .input-area { background: var(--card); padding: 15px; display: flex; gap: 10px; border-top: 1px solid #333; }
            input { flex: 1; background: #2c2c2c; border: none; padding: 12px; border-radius: 25px; color: white; outline: none; }
            button { background: var(--primary); border: none; padding: 10px 20px; border-radius: 25px; color: white; cursor: pointer; font-weight: bold; }
            button:disabled { background: #555; }
            .loading { font-size: 12px; color: #888; margin-top: 5px; }
        </style>
    </head>
    <body>
        <header>
            <h2>ذكائي الاصطناعي الخاص 🤖</h2>
        </header>

        <div id="chat-container">
            <div class="message ai">مرحباً! أنا جاهز لمساعدتك، اسألني أي شيء.</div>
        </div>

        <div class="input-area">
            <input type="text" id="userInput" placeholder="اكتب رسالتك هنا..." onkeypress="if(event.key==='Enter') askAI()">
            <button id="sendBtn" onclick="askAI()">إرسال</button>
        </div>

        <script>
            async function askAI() {
                const inputField = document.getElementById('userInput');
                const chatContainer = document.getElementById('chat-container');
                const sendBtn = document.getElementById('sendBtn');
                const message = inputField.value.trim();

                if (!message) return;

                // إضافة رسالة المستخدم للواجهة
                appendMessage(message, 'user');
                inputField.value = '';
                inputField.disabled = true;
                sendBtn.disabled = true;

                // إضافة مكان لرد الذكاء الاصطناعي
                const aiMsgDiv = appendMessage('جاري التفكير...', 'ai');

                try {
                    const response = await fetch('/chat?user_message=' + encodeURIComponent(message));
                    const data = await response.json();
                    aiMsgDiv.innerText = data.response || "حدث خطأ في الرد";
                } catch (err) {
                    aiMsgDiv.innerText = "فشل الاتصال بالسيرفر";
                } finally {
                    inputField.disabled = false;
                    sendBtn.disabled = false;
                    inputField.focus();
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }

            function appendMessage(text, side) {
                const container = document.getElementById('chat-container');
                const div = document.createElement('div');
                div.className = 'message ' + side;
                div.innerText = text;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
                return div;
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat")
def chat(user_message: str):
    try:
        # توجيه الـ AI ليتحدث بالعربية دائماً وبأسلوب المساعد الشخصي
        response = model.generate_content(f"أجب بالعربية وبشكل مختصر ومفيد: {user_message}")
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}
