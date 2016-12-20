#!/usr/bin/env python
""" load_whiskey.py: Load the website's DB with some dummy data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_db import Base, User, Region, Whiskey



engine = create_engine('sqlite:///whiskey_regions.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



###########################################
# Create 4 dummy users
###########################################
user1 = User(name="Ryan Doe", email="whiskey_man@website.com",
             picture='https://s3.amazonaws.com/uifaces/faces/twitter/mattchevy/128.jpg')
session.add(user1)
session.commit()

user2 = User(name="Ron Burgundy", email="r.rurgundy@website.com",
             picture='http://pbs.twimg.com/profile_images/421045464533073920/ZitK0eZB_reasonably_small.jpeg')
session.add(user2)
session.commit()

user3 = User(name="Lisa Smith", email="whiskey_ladyn@website.com",
             picture='http://lorempixel.com/output/people-q-c-128-128-9.jpg')
session.add(user3)
session.commit()

user4 = User(name="Mark Twain", email="whiskey_writer@website.com",
             picture='https://38.media.tumblr.com/avatar_aeee17e80b56_128.png')
session.add(user4)
session.commit()
###########################################
# add America region and add some whiskey
###########################################
america = Region(user_id=1, name="America")
session.add(america)
session.commit()

whiskey1 = Whiskey(user_id=1, name="Woodford Reserve", description="A brand of premium small batch Kentucky Straight Bourbon Whiskey produced by the Brown-Forman Corporation.", manufacturer="Brown-Forman", type="Small batch Kentucky Straight Bourbon Whiskey", abv="45.20", region=america.name)
session.add(whiskey1)
session.commit()

whiskey2 = Whiskey(user_id=1, name="Town Branch Bourbon", description="Town Branch is a Kentucky straight bourbon whiskey brand produced by the Lexington Brewing and Distilling Company of Lexington, Kentucky which is owned by Alltech. Town Branch Distillery is the first distillery to be built in Lexington in more than 100 years.", manufacturer="Alltech's Lexington Brewing and Distilling Company", type="Kentucky Straight Bourbon Whiskey", abv="40.00", region=america.name)
session.add(whiskey2)
session.commit()

whiskey3 = Whiskey(user_id=1, name="Heaven Hill", description="Heaven Hill Distilleries, Inc. is a private family-owned and operated distillery company headquartered in Bardstown, Kentucky that produces and markets the Heaven Hill brand of Kentucky Straight Bourbon Whiskey and a variety of other distilled spirits.", manufacturer="Heaven Hill", type="Kentucky Straight Bourbon Whiskey", abv="40.00", proof="80", region=america.name)
session.add(whiskey3)
session.commit()

###########################################
# add Scotland and scotish whiskey
###########################################
scotland = Region(user_id=2, name="Scotland")
session.add(scotland)
session.commit()

whiskey4 = Whiskey(user_id=2, name="Glenmorangie", description="The Glenmorangie Company Ltd, whose main product is the range of Glenmorangie single malt whisky. Glenmorangie is categorised as a Highland distillery and boasts the tallest stills in Scotland.", manufacturer="Brown-Forman", type="Single malt", abv="40.00 - 46.00", region=scotland.name)
session.add(whiskey4)
session.commit()

whiskey5 = Whiskey(user_id=2, name="Oban", description="Oban distillery is a whisky distillery in the Scottish west coast port of Oban. Established in 1794, it was built before the town of the same name, which sprung up later in the surrounding craggy harbour.", manufacturer="Diageo", type="West Highland", abv="43.00", region=scotland.name)
session.add(whiskey5)
session.commit()

whiskey6 = Whiskey(user_id=2, name="Johnnie Walker Scotch Black", description="Johnnie Walker is a brand of Scotch whisky owned by Diageo that originated in Kilmarnock, Ayrshire, Scotland. It is the most widely distributed brand of blended Scotch whisky in the world, sold in almost every country, with annual sales of over 130 million bottles.", manufacturer="Diageo", type="Scotch", abv="40.00", region=scotland.name)
session.add(whiskey6)
session.commit()

###########################################
# add Australia region and whiskey
###########################################
australia = Region(user_id=2, name="Australia")
session.add(australia)
session.commit()

whiskey7 = Whiskey(user_id=2, name="Timboon \"Port Expression\"", description="Tasting Notes: Golden straw soft pink colour. The nose is gentle and inviting, with aromas of oak, caramel, butter scotch, dark chocolate, red berries, honey, the palate is soft with citrus overtones.", manufacturer="Railway Shed Distillery", type="Single Malt", abv="44.00", region=australia.name)
session.add(whiskey7)
session.commit()

whiskey8 = Whiskey(user_id=2, name="Archie Rose White Rye", description="This White Rye is uniquely distilled from rare malted rye and barley sourced from the finest producers, and greets you with cinnamon, nutmeg and spicy notes that envelope the palate. Twice distilled, it features a lingering, buttery finish with a subtle smokiness, and can be savoured straight or in your cocktail of choice.", manufacturer="Archie Rose Distillery", type="White Rye", abv="40.00", region=australia.name)
session.add(whiskey8)
session.commit()



###########################################
# add Canada region and whiskey
###########################################
canada = Region(user_id=3, name="Canada")
session.add(canada)
session.commit()

whiskey9 = Whiskey(user_id=3, name="Canadian Club", description="Spicy and zesty, complimented with hints of rich oak and sweet vanilla, pleasant sweetness", manufacturer="Beam Suntory", type="Canadian whisky", abv="40.00", region=canada.name)
session.add(whiskey9)
session.commit()

###########################################
# add India region and whiskey
###########################################
india = Region(user_id=1, name="India")
session.add(india)
session.commit()

###########################################
# add Ireland region and whiskey
###########################################
ireland = Region(user_id=3, name="Ireland")
session.add(ireland)
session.commit()

whiskey10 = Whiskey(user_id=3, name="Paddy", description="Paddy Whiskey is a brand of 80-proof blended Irish whiskey produced in Cork, Ireland, by the company Irish Distillers. It is Ireland's third best selling whiskey.", manufacturer="Irish Distillers(Pernod Ricard)", type="Irish Whisky", abv="40.00", region=ireland.name)
session.add(whiskey10)
session.commit()

whiskey11 = Whiskey(user_id=3, name="Jameson", description="Jameson is a blended Irish whiskey produced by the Irish Distillers subsidiary of Pernod Ricard.", manufacturer="Irish Distillers(Pernod Ricard)", type="Irish Whisky", abv="40.00", region=ireland.name)
session.add(whiskey11)
session.commit()

whiskey12 = Whiskey(user_id=3, name="Kilbeggan", description="Easy going and approachable, but with its own distinctive style. The finest grain and malt whiskeys are blended together for a smooth, sweet taste and lovely malt finish, a characteristic of our 180 year old pot still that is at the heart of Kilbeggan Irish whiskey.", manufacturer="Kilbeggan Distilling Company", type="Irish Whisky", abv="40.00", region=ireland.name)
session.add(whiskey12)
session.commit()

###########################################
# add Japan region and whiskey
###########################################
japan = Region(user_id=1, name="Japan")
session.add(japan)
session.commit()


print "whiskey added!"
