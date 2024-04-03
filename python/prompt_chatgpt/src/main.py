import os
from openai import OpenAI
from .utils import get_static_file, throw_if_missing


def main(context):
    throw_if_missing(os.environ, ["OPENAI_API_KEY"])

    if context.req.method == "GET":
        return context.res.send(
            get_static_file("index.html"),
            200,
            {
                "content-type": "text/html; charset=utf-8"
            },
        )

    try:
        throw_if_missing(context.req.body, ["prompt"])
    except ValueError as err:
        return context.res.json({"ok": False, "error": err.message}, 400)

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    if os.environ.get("API_BASE_URL"):
        client.base_url = os.environ.get("API_BASE_URL")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
            messages=[{"role": "user", "content": context.req.body["prompt"]}],
        )
        completion = response.choices[0].message.content
        return context.res.json({"ok": True, "completion": completion}, 200)

    except Exception as err:
        return context.res.json({"ok": False, "error": err.message}, 500)
