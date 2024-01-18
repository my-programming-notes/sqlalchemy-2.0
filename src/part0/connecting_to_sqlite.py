"""
Code for Chapter 2: Connecting to SQLite.
"""
from sqlalchemy import create_engine, text

# using transient memory as storage
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# use a file "store.db" to store SQLite's data
engine = create_engine("sqlite+pysqlite:///store.db", echo=True)

# connect to the database and write our first message
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE messages (x varchar(16), y varchar(16))"))
    conn.execute(
        text("INSERT INTO messages (x, y) VALUES (:x, :y)"),
        [{"x": "Hello", "y": "World"}],
    )
    conn.commit()
