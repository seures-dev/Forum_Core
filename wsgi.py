from application import app
from config import Config

if __name__ == '__main__':
    app.run(debug=True, port=Config.get_host_port())
