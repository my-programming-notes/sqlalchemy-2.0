"""
Code for Chapter 2: Connecting to PostgreSQL.
"""
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://postgres:pw2023@localhost:5432/test",
    echo=True,
)

# connect to the database and write our first message
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE messages (x varchar(16), y varchar(16))"))
    conn.execute(
        text("INSERT INTO messages (x, y) VALUES (:x, :y)"),
        [{"x": "Hello", "y": "World"}],
    )
    conn.commit()
