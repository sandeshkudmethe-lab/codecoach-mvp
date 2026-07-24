from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("--- TESTING GEMINI API KEY ---")

try:
    test_model = "gemini-3.5-flash"
    print(f"Testing generation using '{test_model}'...")
    
    response = client.models.generate_content(
        model=test_model,
        contents="Say 'Hello, API is working!'"
    )
    print(f"\n🎉 Model Output:\n{response.text}")

except Exception as e:
    print(f"\n❌ API Connection Failed:\n{e}")