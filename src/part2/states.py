"""
Code for Chapter 9: Using the Session

Session state transitions.
"""
from models import Base, Employee, SessionMaker, engine
from sqlalchemy import inspect

# optional, start from a clean state
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = SessionMaker()

nobody = Employee(name="Nobody")
print("STATE: transient", inspect(nobody).transient)  # True

session.add(nobody)
print("STATE: pending", inspect(nobody).pending)  # True

print(session.new)
# prints IdentitySet([Employee(employee_id=None, manager_id=None,
# name='Nobody', is_manager=False, hire_date=None)])

print("Object in session:", nobody in session)  # True

session.flush()
print("STATE: persistent", inspect(nobody).persistent)  # True

print(session.get(Employee, nobody.employee_id))
# prints Employee(employee_id=1, manager_id=None, name='Nobody',
# is_manager=False, hire_date=datetime.date(2023, 8, 1))

session.delete(nobody)
session.flush()
print("STATE: deleted", inspect(nobody).deleted)  # True

session.commit()
session.close()
print("STATE: detached", inspect(nobody).detached)  # True
