from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://jtrbebwzyskmln:53f8e7c7e4f65fe9ca30ff1741dccfc1d95f46aaeb761b1c38f0a19217d64e1a@ec2-54-155-87-214.eu-west-1.compute.amazonaws.com:5432/dcbo0o6er550eq"
db = SQLAlchemy(app)
