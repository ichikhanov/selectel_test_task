class Queries(object):
    def __init__(self):
        self.create_ticket = """INSERT INTO tickets (theme, text,
                                                     email, status)
                                 VALUES (%(theme)s, %(text)s,
                                         %(email)s, %(status)s)
                                         RETURNING *;"""
        self.get_ticket_by_id = """SELECT * FROM tickets where id = %s"""
        self.get_comments_by_ticket = """SELECT * FROM comments
                                          WHERE ticket_id = %s;"""
        self.update_ticket_status = """UPDATE tickets SET status = %s
                                        WHERE id = %s RETURNING *;"""
        self.create_comment = """INSERT INTO comments (email, text, ticket_id)
                                  VALUES(%(email)s, %(text)s,
                                  (SELECT id FROM tickets
                                    WHERE id = %(ticket_id)s
                                     AND status <> 'closed'))
                                   RETURNING *;"""
