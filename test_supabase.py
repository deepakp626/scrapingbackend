import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)
print("KEY EXISTS:", bool(key))

supabase = create_client(url, key)

try:

    result = (
        supabase.storage
        .from_("blog-thumbnail")
        .upload(
            path="test-image.txt",
            file=b"hello",
            file_options={
                "content-type": "text/plain",
                "upsert": "true",
            },
        )
    )

    print("SUCCESS")
    print(result)

except Exception as e:

    print("FAILED")
    print("TYPE:", type(e))
    print("ERROR:", repr(e))

    if hasattr(e, "response"):

        print("STATUS:", e.response.status_code)
        print("HEADERS:", e.response.headers)
        print("BODY:", e.response.text)
