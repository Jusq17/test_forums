from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://hebkoqcpdlrzrs:1c17dbeda6730c8f7dbb96d5f0d029020fd2cef206066e8d3427e53f2a15902e@ec2-54-217-15-9.eu-west-1.compute.amazonaws.com:5432/daqrrbc4dh7bb8"
db = SQLAlchemy(app)
