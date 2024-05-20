import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

def create_database(db_name):
    engine = create_engine(f'sqlite:///{db_name}.sqlite3', echo=True)
    Base.metadata.create_all(engine)
    print(f"Database '{db_name}.sqlite3' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_database.py <database_name>")
        sys.exit(1)

    db_name = sys.argv[1]
    create_database(db_name)
