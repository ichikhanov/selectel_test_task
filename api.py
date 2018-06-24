import json
import datetime
from utils import (
    get_db_cursor,
    error_handler,
    ValidationException,
    InternalServerError,
    MEMCACHE_URL,
    MEMCACHE_PORT,
)
from queries import Queries
from validator import CerberusValidator
from psycopg2 import IntegrityError
import memcache

mc = memcache.Client(["{0}:{1}".format(MEMCACHE_URL, MEMCACHE_PORT)], debug=0)


class API(object):
    def __init__(self):
        self.validator = CerberusValidator()
        self.queries = Queries()
        self.mc = mc

    def datetime_converter(self, item):
        if isinstance(item, datetime.datetime):
            return item.__str__()

    def get_from_cache(self, key):
        obj = self.mc.get(key)
        return obj

    def set_to_cache(self, key, value):
        self.mc.set(key, value)

    def prepare_request_data(self, request):
        if request.data:
            return json.loads(request.data)
        elif request.form:
            return request.form.to_dict()
        else:
            raise ValidationException("Empty request")

    def check_ticket_patch_logic(self, ticket_id, status, cursor):
        cursor.execute(self.queries.get_ticket_by_id, (ticket_id,))
        ticket = cursor.fetchone()
        if not ticket:
            raise IndexError
        origin_status = ticket["status"]
        if origin_status == "closed":
            raise ValidationException(
                "Mailformed status, you are not aloowed to modify clodes tickets"
            )
        if origin_status == "open":
            if status not in ["responded", "closed"]:
                raise ValidationException(
                    "Mailformed status, allowed: {0}".format(["responsed", "closed"])
                )
        elif origin_status == "responsed":
            if status not in ["waiting_for_response", "closed"]:
                raise ValidationException(
                    "Mailformed status, allowed: {0}".format(
                        ["waiting_for_response", "closed"]
                    )
                )
        else:
            raise InternalServerError("Unexpected status change: {0}".format(status))

    def get_ticket_with_comments(self, ticket_id, cursor):
        cursor.execute(self.queries.get_ticket_by_id, (ticket_id,))
        ticket = cursor.fetchone()
        if not ticket:
            raise IndexError
        cursor.execute(self.queries.get_comments_by_ticket, (ticket_id,))
        comments = cursor.fetchall() or []
        ticket.update({"comments": comments})
        return ticket

    @error_handler()
    def get_ticket(self, ticket_id):
        ticket = self.get_from_cache("ticket_{0}".format(ticket_id))
        if ticket:
            return json.dumps(ticket, default=self.datetime_converter), 200
        with get_db_cursor() as cursor:
            ticket = self.get_ticket_with_comments(ticket_id, cursor)
            self.set_to_cache("ticket_{0}".format(ticket_id), ticket)
        return json.dumps(ticket, default=self.datetime_converter), 200

    @error_handler()
    def post_ticket(self, request):
        data = self.prepare_request_data(request)
        data = self.validator.validate_ticket_post_schema(data)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(self.queries.create_ticket, data)
            ticket = cursor.fetchone()
            ticket.update({"comments": []})
            self.set_to_cache("ticket_{0}".format(ticket["id"]), ticket)
        return json.dumps(ticket, default=self.datetime_converter), 201

    @error_handler()
    def patch_ticket(self, ticket_id, request):
        data = self.validator.validate_ticket_patch_schema(
            self.prepare_request_data(request)
        )
        status = data["status"]
        with get_db_cursor(commit=True) as cursor:
            self.check_ticket_patch_logic(ticket_id, status, cursor)
            cursor.execute(self.queries.update_ticket_status, (status, ticket_id))
            ticket = cursor.fetchone()
            cursor.execute(self.queries.get_comments_by_ticket, (ticket_id,))
            comments = cursor.fetchall() or []
            ticket.update({"comments": comments})
            self.set_to_cache("ticket_{0}".format(ticket_id), ticket)
        return json.dumps(ticket, default=self.datetime_converter), 200

    @error_handler()
    def post_comment(self, request):
        data = self.validator.validate_comment_post_schema(
            self.prepare_request_data(request)
        )
        with get_db_cursor(commit=True) as cursor:
            try:
                cursor.execute(self.queries.create_comment, data)
            except IntegrityError:
                raise ValidationException(
                    "You are not allowed create comments for closed tickets"
                )
            comment = cursor.fetchone()
            self.set_to_cache(
                "ticket_{0}".format(comment["ticket_id"]),
                self.get_ticket_with_comments(comment["ticket_id"], cursor),
            )
        return json.dumps(comment, default=self.datetime_converter), 201
