"""
FastAPI main application for Hisaab WhatsApp Voice Assistant
"""
import os
from fastapi import FastAPI, Request, Response, status
import httpx
from dotenv import load_dotenv
from langsmith import traceable

from app.agent.graph import agent
from app.whatsapp import send_whatsapp_text, send_whatsapp_audio
from app.voice import generate_voice_message, transcribe_voice

# Load environment variables
load_dotenv()

# Environment variables
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
UPLIFT_API_KEY = os.getenv("UPLIFT_API_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI app
app = FastAPI(title="Hisaab AI Assistant", version="1.0.0")


@app.get("/webhook")
async def verify_webhook(request: Request):
    """WhatsApp webhook verification"""
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    mode = request.query_params.get("hub.mode")
    
    if verify_token == WEBHOOK_VERIFY_TOKEN:
        print("✅ Token matches! Sending challenge back")
        return Response(content=challenge, media_type="text/plain")
    else:
        print("❌ Token mismatch! Returning 403")
        return Response(status_code=status.HTTP_403_FORBIDDEN)


@app.get("/proxy-audio")
async def proxy_audio(url: str):
    """Proxy audio files for WhatsApp"""
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return Response(content=r.content, media_type="audio/mpeg")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    print("\n" + "=" * 50)
    print("📨 POST /webhook - Message received")

    try:
        body = await request.json()
        print(f"Full body: {body}")

        entry = body.get("entry", [])
        if not entry:
            return Response(status_code=status.HTTP_200_OK)

        changes = entry[0].get("changes", [])
        if not changes:
            return Response(status_code=status.HTTP_200_OK)

        value = changes[0].get("value", {})
        messages = value.get("messages")

        if messages:
            message = messages[0]
            from_number = message.get("from")
            msg_type = message.get("type")

            if msg_type == "text":
                text = message.get("text", {}).get("body")
                if text:
                    print(f"🔄 Processing text from {from_number}: {text}")
                    await handle_message(from_number, text)

            elif msg_type == "audio":
                media_id = message["audio"]["id"]
                mime_type = message["audio"]["mime_type"]
                print(f"🎤 Received audio note (media_id={media_id}, mime={mime_type})")
                
                transcription = await transcribe_voice(media_id, WHATSAPP_ACCESS_TOKEN, OPENAI_API_KEY)
                if transcription:
                    await handle_message(from_number, transcription)
                else:
                    print("⚠️ Failed to transcribe audio")

        return Response(status_code=status.HTTP_200_OK)

    except Exception as e:
        print(f"❌ ERROR in webhook handler: {str(e)}")
        return Response(status_code=status.HTTP_200_OK)


@traceable
async def handle_message(phone_number: str, user_message: str):
    """Handle individual message processing"""
    try:
        # Generate response using agent
        response_text = generate_response(user_message, phone_number)
        
        # Send text response
        await send_whatsapp_text(
            phone_number, 
            response_text, 
            PHONE_NUMBER_ID, 
            WHATSAPP_ACCESS_TOKEN
        )
        
        # Generate and send voice response
        audio_url = await generate_voice_message(response_text, UPLIFT_API_KEY)
        await send_whatsapp_audio(
            phone_number, 
            audio_url, 
            PHONE_NUMBER_ID, 
            WHATSAPP_ACCESS_TOKEN,
            "https://a98ce46c01fc.ngrok-free.app"  # Replace with your ngrok URL
        )
        
        print(f"✅ Message handled for phone: {phone_number}")

    except Exception as e:
        print(f"❌ ERROR in handle_message: {str(e)}")


@traceable
def generate_response(user_message: str, phone_number: str) -> str:
    """Generate response using LangGraph agent"""
    config = {"configurable": {"thread_id": phone_number}}
    response = agent.invoke(
        {
            "messages": [{"role": "user", "content": user_message}], 
            "phone_number": phone_number
        }, 
        config
    )
    return response["messages"][-1].content


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
