CREATE OR REPLACE FUNCTION updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE sequence tickets_serial START 1;

CREATE table tickets (
    id  integer PRIMARY KEY DEFAULT nextval('tickets_serial'),
    created_at timestamp  NOT NULL  DEFAULT current_timestamp,
    updated_at timestamp  NOT NULL  DEFAULT current_timestamp,
    theme VARCHAR(255) NOT NULL,
    text text NOT NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE sequence comments_serial START 1;

CREATE table comments (
    id  integer PRIMARY KEY DEFAULT nextval('comments_serial'),
    created_at timestamp  NOT NULL  DEFAULT current_timestamp,
    ticket_id integer REFERENCES tickets (id) NOT NULL,
    email VARCHAR(255) NOT NULL,
    text text NOT NULL
);

CREATE TRIGGER updated_at_tickets BEFORE UPDATE
    ON tickets FOR EACH ROW EXECUTE PROCEDURE
    updated_at_column();

