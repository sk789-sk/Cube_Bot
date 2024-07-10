# Standard library imports

# Remote library imports
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import secrets

# Local imports

# Instantiate app, set attributes

load_dotenv()

app = Flask(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


DB_main = f'postgresql://{os.getenv("RDS_username_main")}:{os.getenv("RDS_pass_main")}@{os.getenv("RDS_endpoint_main")}/{os.getenv("RDS_db_name_main")}' #test_DB_name or DB_name

LocalDB_test = f'postgresql://{os.getenv("DB_Username")}:{os.getenv("DB_Password")}@{os.getenv("DB_Host")}/NYC_Cube' #test_DB_name or DB_name {os.getenv("DB_name")}

# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = LocalDB_test


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.config['SECRET_KEY'] = secrets.token_hex(32)

# secret_key = secrets.token_hex(32)


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Define metadata, instantiate db
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

db.init_app(app)

# Instantiate REST API
#api = Api(app)

# Instantiate CORS
CORS(app)
