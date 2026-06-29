from service.rag_api import app as api
from view.app import create_app as front
import uvicorn
import threading

class Application:
    def __init__(self):
        self.front = front()
        self.api = api

    def __call__(self):
        def run_flask():
            self.front.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

        def run_fastapi():
            uvicorn.run(self.api, host="0.0.0.0", port=8000, log_level="info")

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)

        flask_thread.start()
        fastapi_thread.start()

        flask_thread.join()
        fastapi_thread.join()


if __name__ == "__main__":
    app = Application()
    app.run()
