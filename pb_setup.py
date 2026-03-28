import httpx
import json
import asyncio

async def setup():
    async with httpx.AsyncClient() as client:
        # Create admin
        try:
            r1 = await client.post('http://127.0.0.1:8090/api/admins', json={"email":"admin@test.com", "password":"adminpassword123", "passwordConfirm":"adminpassword123"})
            print("Admin created:", r1.status_code)
        except:
            pass
            
        r2 = await client.post('http://127.0.0.1:8090/api/admins/auth-with-password', json={"identity":"admin@test.com", "password":"adminpassword123"})
        token = r2.json().get('token')
        print("Logged in, token:", token[:10])
        
        with open('pocketbase_schema.json', encoding="utf-8") as f:
            collections = json.load(f)
            
        r3 = await client.put('http://127.0.0.1:8090/api/collections/import', json={"collections": collections, "deleteMissing": False}, headers={"Authorization": f"Bearer {token}"})
        print("Imported collections:", r3.status_code, r3.text)
        
        # Insert a friction
        r4 = await client.post('http://127.0.0.1:8090/api/collections/fricciones/records', json={"description": "Odio ver tutoriales interminables para configurar servidores web, siempre me olvido y pierdo horas leyendo foros.", "severity": 4})
        print("Inserted friction:", r4.status_code)

if __name__ == "__main__":
    asyncio.run(setup())
