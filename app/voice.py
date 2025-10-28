"""
Voice generation and transcription utilities
"""
import io
import httpx
from openai import OpenAI
from typing import Optional
import traceback


async def generate_voice_message(text: str, api_key: str) -> str:
    """Generate voice message using Uplift AI TTS"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            request_data = {
                "voiceId": "v_8eelc901",
                "text": text,
                "outputFormat": "MP3_22050_128"
            }
            
            response = await client.post(
                "https://api.upliftai.org/v1/synthesis/text-to-speech-async",
                json=request_data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Uplift AI error: {response.text}")
            
            data = response.json()
            media_id = data["mediaId"]
            token = data["token"]
            
            audio_url = f"https://api.upliftai.org/v1/synthesis/stream-audio/{media_id}?token={token}"
            print(f"✅ Audio URL generated: {audio_url}")
            
            return audio_url
            
    except Exception as e:
        print(f"❌ ERROR in generate_voice_message: {str(e)}")
        print(traceback.format_exc())
        raise


async def transcribe_voice(media_id: str, access_token: str, openai_api_key: str) -> Optional[str]:
    """Transcribe voice message using OpenAI Whisper"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1️⃣ Get downloadable URL
            media_url_resp = await client.get(
                f"https://graph.facebook.com/v17.0/{media_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            media_url_resp.raise_for_status()
            media_url = media_url_resp.json()["url"]

            # 2️⃣ Download audio bytes directly
            audio_resp = await client.get(
                media_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            audio_resp.raise_for_status()
            audio_bytes = io.BytesIO(audio_resp.content)

        # 3️⃣ Transcribe directly from memory
        openai_client = OpenAI(api_key=openai_api_key)
        transcript = openai_client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", 
            file=("audio.ogg", audio_bytes),
            language="ur"
        )
        
        return transcript.text.strip()

    except Exception as e:
        print(f"❌ ERROR in transcribe_voice: {str(e)}")
        print(traceback.format_exc())
        return None
