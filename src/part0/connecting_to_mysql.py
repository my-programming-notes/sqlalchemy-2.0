"""
Code for Chapter 2: Connecting to MySQL.
"""
from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://root:pw2023@localhost/test",
    echo=True,
    pool_recycle=3600,
)

# connect to the database and write our first message
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE messages (x varchar(16), y varchar(16))"))
    conn.execute(
        text("INSERT INTO messages (x, y) VALUES (:x, :y)"),
        [{"x": "Hello", "y": "World"}],
    )
    conn.commit()
