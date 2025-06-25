#!/usr/bin/env python
"""
load_whiskey.py: Populate the whiskey_regions.db SQLite database
with sample user, region, and whiskey entries.
"""

from db_models import Base, Region, User, Whiskey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------------------------
# Setup the database engine and session
# -------------------------------------------
engine = create_engine('sqlite:///whiskey_regions.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(
    name="Ryan Doe",
    email="whiskey_man@website.com",
    picture="https://randomuser.me/api/portraits/men/40.jpg"
)
user2 = User(
    name="Ron Burgundy",
    email="r.rurgundy@website.com",
    picture="http://pbs.twimg.com/profile_images/421045464533073920/ZitK0eZB_reasonably_small.jpeg"
)
user3 = User(
    name="Lisa Smith",
    email="whiskey_ladyn@website.com",
    picture="https://randomuser.me/api/portraits/women/61.jpg"
)
user4 = User(
    name="Mark Twain",
    email="whiskey_writer@website.com",
    picture="https://randomuser.me/api/portraits/men/1.jpg"
)
def add_users(): 
    # -------------------------------------------
  # Add Sample Users
  # -------------------------------------------
  session.add(user1) 
  session.add(user2)  
  session.add(user3)
  session.add(user4)
  session.commit()


def seed():
    add_users()
    # -------------------------------------------
    # Add Regions and Associated Whiskeys
    # -------------------------------------------
    america = Region(user_id=1, name="America")
    session.add(america)
    session.commit()

    session.add_all([
    Whiskey(
    user_id=1,
    name="Woodford Reserve",
    description="A brand of premium small batch Kentucky Straight Bourbon Whiskey...",
    manufacturer="Brown-Forman",
    type="Small batch Kentucky Straight Bourbon Whiskey",
    abv="45.20",
    region=america
    ),
    Whiskey(
    user_id=1,
    name="Town Branch Bourbon",
    description="Produced by Lexington Brewing and Distilling Co of Kentucky...",
    manufacturer="Alltech's Lexington Brewing and Distilling Company",
    type="Kentucky Straight Bourbon Whiskey",
    abv="40.00",
    region=america
    ),
    Whiskey(
    user_id=1,
    name="Heaven Hill",
    description="Heaven Hill Distilleries, family-owned distillery in Bardstown, Kentucky...",
    manufacturer="Heaven Hill",
    type="Kentucky Straight Bourbon Whiskey",
    abv="40.00",
    proof="80",
    region=america
    )
    ])
    session.commit()

    # --- Scotland --- 
    scotland = Region(user_id=2, name="Scotland")
    session.add(scotland)
    session.commit()

    session.add_all([
    Whiskey(
        user_id=2,
        name="Glenmorangie",
        description="Single malt Highland whisky with the tallest stills in Scotland.",
        manufacturer="Brown-Forman",
        type="Single malt",
        abv="40.00 - 46.00",
        region=scotland
    ),
    Whiskey(
        user_id=2,
        name="Oban",
        description="Historic distillery on Scotland's west coast, founded in 1794.",
        manufacturer="Diageo",
        type="West Highland",
        abv="43.00",
        region=scotland
    ),
    Whiskey(
        user_id=2,
        name="Johnnie Walker Scotch Black",
        description="World-renowned blended Scotch whisky by Diageo.",
        manufacturer="Diageo",
        type="Scotch",
        abv="40.00",
        region=scotland
    )
    ])
    session.commit()

    # --- Australia ---
    australia = Region(user_id=2, name="Australia")
    session.add(australia)
    session.commit()

    session.add_all([
    Whiskey(
        user_id=2,
        name='Timboon "Port Expression"',
        description="Golden straw color. Notes of oak, caramel, berries, and citrus.",
        manufacturer="Railway Shed Distillery",
        type="Single Malt",
        abv="44.00",
        region=australia
    ),
    Whiskey(
        user_id=2,
        name="Archie Rose White Rye",
        description="Spicy and buttery rye with a smoky finish. Twice distilled.",
        manufacturer="Archie Rose Distillery",
        type="White Rye",
        abv="40.00",
        region=australia
    )
    ])
    session.commit()

    # --- Canada ---
    canada = Region(user_id=3, name="Canada")
    session.add(canada)
    session.commit()

    whiskey_canada = Whiskey(
    user_id=3,
    name="Canadian Club",
    description="Spicy and zesty with sweet vanilla and oak notes.",
    manufacturer="Beam Suntory",
    type="Canadian whisky",
    abv="40.00",
    region=canada
    )
    session.add(whiskey_canada)
    session.commit()

    # --- India ---
    india = Region(user_id=1, name="India")
    session.add(india)
    session.commit()

    # --- Ireland ---
    ireland = Region(user_id=3, name="Ireland")
    session.add(ireland)
    session.commit()

    session.add_all([
    Whiskey(
        user_id=3,
        name="Paddy",
        description="Smooth 80-proof Irish whiskey from Cork.",
        manufacturer="Irish Distillers (Pernod Ricard)",
        type="Irish Whisky",
        abv="40.00",
        region=ireland
    ),
    Whiskey(
        user_id=3,
        name="Jameson",
        description="Iconic blended Irish whiskey from Irish Distillers.",
        manufacturer="Irish Distillers (Pernod Ricard)",
        type="Irish Whisky",
        abv="40.00",
        region=ireland
    ),
    Whiskey(
        user_id=3,
        name="Kilbeggan",
        description="Sweet and smooth Irish whiskey from 180-year-old pot still.",
        manufacturer="Kilbeggan Distilling Company",
        type="Irish Whisky",
        abv="40.00",
        region=ireland
    )
    ])
    session.commit()

    # --- Japan ---
    japan = Region(user_id=1, name="Japan")
    session.add(japan)
    session.commit()

    # -------------------------------------------
    # Done!
    # -------------------------------------------
    print("Whiskey data loaded successfully!")




