from server import server
from waitress import serve
from dotenv import load_dotenv
import os

load_dotenv()

print("Serving on http://localhost:3000", flush=True)
serve(server, host=os.environ['HOST'], port=os.environ['PORT'])