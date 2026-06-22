import argparse
import os
import sys

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
FRICTIONLOG_API_KEY = os.getenv("FRICTIONLOG_API_KEY")


def main():
    parser = argparse.ArgumentParser(
        description="FrictionLog CLI - Registra fricciones desde la terminal."
    )
    parser.add_argument("comando", choices=["log"], help="Comando a ejecutar")
    parser.add_argument("descripcion", type=str, help="Descripción de la fricción")
    parser.add_argument("--severity", type=int, default=3, help="Nivel de severidad (1-5)")
    parser.add_argument("--api", type=str, default=API_URL, help="URL base de la API")
    parser.add_argument("--api-key", type=str, default=FRICTIONLOG_API_KEY, help="API Key")

    args = parser.parse_args()

    if args.comando == "log":
        if len(args.descripcion) < 10:
            print("Error: La descripción debe tener al menos 10 caracteres.")
            sys.exit(1)

        headers = {}
        if args.api_key:
            headers["Authorization"] = f"Bearer {args.api_key}"

        try:
            with httpx.Client() as client:
                r = client.post(
                    f"{args.api}/registrar-friccion",
                    json={"description": args.descripcion, "severity": args.severity},
                    headers=headers,
                )
                if r.status_code == 200:
                    data = r.json()
                    print(f"Fricción registrada exitosamente! ID: {data.get('id')}")
                else:
                    print(f"Error (HTTP {r.status_code}): {r.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")


if __name__ == "__main__":
    main()
