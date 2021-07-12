from flask import Flask

app = Flask(__name__)
app.secret_key = "6167e8907643abb40209aeb834bdc6c1"

import routes
