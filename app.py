from flask import Flask

app = Flask(__name__)
app.secret_key = "ad0b6b9e97655eff31e35ba1ba2e0f82"

import routes
