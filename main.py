from flask import Flask, request
from api import API


app = Flask(__name__)
methods = API()


@app.route("/tickets", methods=["POST"])
def post_ticket():
    return methods.post_ticket(request)


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    return methods.get_ticket(ticket_id)


@app.route("/tickets/<int:ticket_id>", methods=["PATCH"])
def patch_ticket(ticket_id):
    return methods.patch_ticket(ticket_id, request)


@app.route("/comments", methods=["POST"])
def post_comment():
    return methods.post_comment(request)
