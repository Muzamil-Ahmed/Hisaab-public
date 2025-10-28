"""
WhatsApp API utilities and message handling
"""
import httpx
from fastapi import Response
from typing import Optional
import traceback


async def send_whatsapp_text(
    to: str, 
    text: str, 
    phone_number_id: str, 
    access_token: str
) -> None:
    """Send text message via WhatsApp API"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"https://graph.facebook.com/v17.0/{phone_number_id}/messages",
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "text",
                    "text": {"body": text}
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            print(f"WhatsApp text sent: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending text: {str(e)}")
        raise


async def send_whatsapp_audio(
    to: str, 
    audio_url: str, 
    phone_number_id: str, 
    access_token: str,
    proxy_url: str
) -> None:
    """Send audio message via WhatsApp API"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            msg_response = await client.post(
                f"https://graph.facebook.com/v17.0/{phone_number_id}/messages",
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "audio",
                    "audio": {"link": f"{proxy_url}/proxy-audio?url={audio_url}"}
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            print(f"WhatsApp audio sent: {msg_response.status_code}")
    except Exception as e:
        print(f"❌ ERROR in send_whatsapp_audio: {str(e)}")
        print(traceback.format_exc())
        raise


async def download_media(media_id: str, access_token: str) -> bytes:
    """Download media from WhatsApp API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Get media URL
        url_resp = await client.get(
            f"https://graph.facebook.com/v17.0/{media_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        url_data = url_resp.json()
        media_url = url_data["url"]

        # Step 2: Download media file
        file_resp = await client.get(
            media_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return file_resp.content
