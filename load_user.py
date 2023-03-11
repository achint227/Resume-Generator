from os import environ
from bson.objectid import ObjectId

import pymongo
from dotenv import load_dotenv

load_dotenv()


db_url = environ.get("DATABASE_URL")

myclient = pymongo.MongoClient(db_url)

db = myclient["Resume"]
collection = db["Resume"]


def all_resumes():
    res = []
    for _ in collection.find():
        _["_id"] = str(_["_id"])
        res.append(_)

    return res


def find_by_id(id):
    document_id = ObjectId(id)
    return collection.find_one({"_id": document_id})


def find_by_name(name):
    return collection.find({"basic_info.name": name})[0]


def find_by_resume_name(name):
    return collection.find({"name": name})[0]


def add_resume(resume):
    return collection.insert_one(resume)
