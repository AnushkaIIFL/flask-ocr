from flask import Flask
from HFC.deed import deed
from HFC.patta import patta
from HFC.ror import ror
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# @app.route('/')
# def index():
#     name = os.getenv('NAME')
#     print(name)
#     return name
app.register_blueprint(deed)
app.register_blueprint(patta)
app.register_blueprint(ror)

if __name__ == '__main__':
    app.run()
