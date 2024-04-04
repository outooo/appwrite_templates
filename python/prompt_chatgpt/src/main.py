import os
import requests
from .utils import get_static_file, throw_if_missing

def main(context):
    throw_if_missing(os.environ, ["OPENAI_API_KEY"])

    if context.req.method == "GET":
        return context.res.send(
            get_static_file("index.html"), 200, {"content-type": "text/html; charset=utf-8"}
        )

    try:
        throw_if_missing(context.req.body, ["prompt"])
    except ValueError as err:
        return context.res.json({"ok": False, "error": err.message}, 400)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    }

    data = {
        "model": os.environ.get('MODEL', "gpt-3.5-turbo"),
        "max_tokens": int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
        "messages": [{"role": "user", "content": context.req.body["prompt"]}],
        "stream": False,
    }

    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com")

    try:
        response = requests.post(f"{api_base_url}/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        completion = response.json()["choices"][0]["message"]["content"]
        return context.res.json({"ok": True, "completion": completion}, 200)
    except requests.exceptions.RequestException as err:
        return context.res.json({"ok": False, "error": str(err)}, 500)
    except Exception as err:
        return context.res.json({"ok": False, "error": str(err) + response.text}, 500)
