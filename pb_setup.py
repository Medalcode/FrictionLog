import asyncio
import json
import os

import httpx

PB_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")
ADMIN_EMAIL = os.getenv("PB_ADMIN_EMAIL", "admin@test.com")
ADMIN_PASSWORD = os.getenv("PB_ADMIN_PASSWORD", "adminpassword123")


async def setup():
    async with httpx.AsyncClient() as client:
        try:
            r1 = await client.post(
                f"{PB_URL}/api/admins",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "passwordConfirm": ADMIN_PASSWORD,
                },
            )
            print("Admin created:", r1.status_code)
        except Exception as e:
            print("Admin setup note:", e)

        r2 = await client.post(
            f"{PB_URL}/api/admins/auth-with-password",
            json={"identity": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        token = r2.json().get("token")
        if not token:
            print("Failed to obtain admin token:", r2.text)
            return
        print("Logged in, token:", token[:10])

        if os.path.exists("pocketbase_schema.json"):
            with open("pocketbase_schema.json", encoding="utf-8") as f:
                collections = json.load(f)

            r3 = await client.put(
                f"{PB_URL}/api/collections/import",
                json={"collections": collections, "deleteMissing": False},
                headers={"Authorization": f"Bearer {token}"},
            )
            print("Imported collections:", r3.status_code, r3.text)

        r4 = await client.post(
            f"{PB_URL}/api/collections/fricciones/records",
            json={
                "description": "Odio configurar servidores web manualmente, pierdo horas.",
                "severity": 4,
            },
        )
        print("Inserted friction:", r4.status_code)


if __name__ == "__main__":
    asyncio.run(setup())

