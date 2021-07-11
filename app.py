from flask import Flask

app = Flask(__name__)
app.secret_key = "932329bc1ed5fb8abee9b91df0a99292"

import routes
