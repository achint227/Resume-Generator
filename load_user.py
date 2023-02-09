from os import environ

import pymongo
from dotenv import load_dotenv

load_dotenv()


db_url = environ.get("DATABASE_URL")

myclient = pymongo.MongoClient(db_url)

db = myclient["Resume"]
collection = db["Resume"]


def find_by_name(name):
    return collection.find({"basic_info.name": name})[0]
