import asyncio
import json
import time
import httpx
import pyotp
import websockets

TOKEN = "TOKENINIZ"
GUILD_ID = "HEDEF_SUNUCU_ID"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
USER_AGENT = "Discord-Android/210000; Samsung Galaxy J3 Prime (SM-J327T1) cfbypass; Android 7.0"

def get_mfa():
    try:
        with open("mfa.txt", "r", encoding="utf-8") as f:
            secret = f.read().strip()
        return pyotp.TOTP(secret).now() if secret else None
    except Exception:
        return None

async def claim(client: httpx.AsyncClient, vanity: str, start_time: float):
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/vanity-url"
    headers = {}
    
    mfa = get_mfa()
    if mfa:
        headers["x-discord-mfa-authorization"] = mfa

    try:
        resp = await client.patch(url, json={"code": vanity}, headers=headers)
        latency = int((time.perf_counter() - start_time) * 1000)
        print(f"[RUST ULTRA LOW LATENCY METHOD] [{latency}ms] [>] {vanity} -> {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[RUST ULTRA LOW LATENCY METHOD] [!] Claim hatası: {e}")

async def main():
    print("[RUST ULTRA LOW LATENCY METHOD] Starting listener...")

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    async with httpx.AsyncClient(http2=True, headers=headers, timeout=10.0) as client:
        try:
            await client.get("https://discord.com/api/v10/users/@me")
            print("[RUST ULTRA LOW LATENCY METHOD] HTTP/2 socket pre-warmed.")
        except Exception:
            pass

        async with websockets.connect(GATEWAY_URL) as ws:
            print("[RUST ULTRA LOW LATENCY METHOD] Gateway connected.")

            async for message in ws:
                if "GUILD_UPDATE" in message:
                    start_time = time.perf_counter()
                    try:
                        data = json.loads(message)
                        if data.get("t") == "GUILD_UPDATE":
                            vanity = data.get("d", {}).get("vanity_url_code")
                            if vanity:
                                asyncio.create_task(claim(client, vanity, start_time))
                    except Exception:
                        pass
                    continue

                try:
                    data = json.loads(message)
                    if data.get("op") == 10:
                        await ws.send(json.dumps({"op": 1, "d": None}))
                        identify = {
                            "op": 2,
                            "d": {
                                "token": TOKEN,
                                "properties": {
                                    "os": "Android",
                                    "browser": "Discord Android",
                                    "device": "Samsung Galaxy J3 Prime (SM-J327T1) cfbypass",
                                },
                                "intents": 1,
                            },
                        }
                        await ws.send(json.dumps(identify))
                except Exception:
                    pass

if __name__ == "__main__":
    asyncio.run(main())
