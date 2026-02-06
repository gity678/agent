from fastapi import FastAPI
import google.generativeai as genai
import os

app = FastAPI()

# جلب المفتاح من إعدادات Railway (Variables)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# اختيار الموديل (Flash سريع ومجاني)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/")
def read_root():
    return {"message": "مرحباً! ذكاؤك الاصطناعي الشخصي يعمل الآن على Railway"}

@app.get("/chat")
def chat(user_message: str):
    try:
        # هنا يمكنك إضافة "تعليمات شخصية" قبل رسالة المستخدم
        # مثلاً: "أنت مساعد مبرمج محترف، أجب بالعربية"
        response = model.generate_content(f"أجب بالعربية: {user_message}")
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}
