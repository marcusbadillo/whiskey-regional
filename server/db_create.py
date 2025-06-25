#!/usr/bin/env python
"""
create_db.py: Uses SQLAlchemy to create the SQLite database and
define ORM models for a whiskey catalog application.
"""
from db_models import Base
from db_seed import seed
from sqlalchemy import create_engine


# ---------------------------------
# Function to Create SQLite DB File
# ---------------------------------
def create_database(db_uri='sqlite:///whiskey_regions.db'):
    """
    Initializes the database using the provided URI.
    By default, creates a local SQLite DB file.
    """

    # -------------------------------------------
    # Setup the database engine and session
    # -------------------------------------------
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)

    print("Database created successfully.")


# -----------------------
# Entry point for script
# -----------------------
if __name__ == '__main__':
    create_database()
    seed()    
