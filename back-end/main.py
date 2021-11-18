from server import server
from waitress import serve

print("Serving on http://localhost:3000", flush=True)
serve(server, host="127.0.0.1", port=3000)