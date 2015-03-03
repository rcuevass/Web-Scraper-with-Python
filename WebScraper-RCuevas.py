#
# SECTION I. Code information 
#
# Web scraper coded by Rogelio Cuevas-Saavedra (rogercuevas.ca@gmail.com)
# First version finished on: Dec 20th-23rd, 2014.
# Second version: Under development
# Program coded as part of the final Leada project on web scraping.
#
###########################################################################################################################
#
# SECTION II. General information about the program.
#
# This program accesses the Boat Trader (R) website "http://www.boattrader.com" and after
# making a simple engine search in the web site (used and new sailing boats in this case),
# the program collects the brand and make, price and contact number of seller of the
# first 800 boats. The info is then stored in the BoatsInfo.csv file. 
# 
########################################################################################################################
#
# SECTION III. Brief description of the website structure.
# 
# 1. We notice that we can control the number of entires displayed in the search. For instance,
#    the link
#    http://www.boattrader.com/search-results/NewOrUsed-used/Type-Sail/Category-all/Region-all/Sort-Length:DESC/Page-1,100
#    displays page number 1 with the info of 100 boats.
#
# 2. Based on the above, we choose to navigate troughout the first 8 pages and collect the needed info in
#    in each of the boats displated in each of these 8 pages. Navigation of these each pages is achieved by modifying
#    /Page-x,100 at the end of the link, where x runs from 1 to 8.
#
# 3. In each of the each pages mentioned above, the model, make and price of the boats is displayed. The price is collected
#    by using Python's Beautifulsoup 
#           http://www.crummy.com/software/BeautifulSoup/
#           http://www.crummy.com/software/BeautifulSoup/bs4/doc/
#
# 4. The phone number is not displayed in the pages described in points 1. and 2; it is obtained by clicking on the orange 
#    "More Info" button displayed at each boat entry. After clicking the make and price is again available
#
# 5. When clicking on the button described in 4, the website re-directs us the the link
#     http://www.boattrader.com/listing/Model_Make, where Model_Make is the "href" string 
#     given by BeautifulSoup in the "main" website listing (the one displaying 100 boats)
#
#
########################################################################################################################
#
# SECTION IV. Brief description of algorithm followed
#
# Based on Section III, we describe the algorithm followed
#
#  1. Access the website
#     http://www.boattrader.com/search-results/NewOrUsed-used/Type-Sail/Category-all/Region-all/Sort-Length:DESC/Page-x,100
#     with x = 1. This website contains the info of the first (x=1) 100 boats.
#     
#  2. For EACH boat displayed by page described in 1, locate and read price of each boat in that page.
#     Use the .find_all in BeautifulSoup
#
#  3. For EACH boat displayed by page described in 1, locate its corresponding orange "More Info" button, get its 
#     href (which has the sructure /listing/Model_Make ), access the link http://www.boattrader.com/listing/Model_Make
#     and obtain the price, make and phone number of the corresponding boat. To get the href and phone number of the boat 
#     we also use .find_all in BeautifulSoup. 
#
#     * Note. The phone number in the HTML source code of the corresponding boat is displayed as a "mirrored" image of the
#             actual phone number. For instance, phone number (987)-654-3210 is actualy read as 0123-456-(789) and must
#             be "mirror-invereted"
#
#  4. After finishing points 2. and 3. for the first hundred boats, increase the value of x and repeat 2. and 3.
#
#  5. Repeat the above algorithm for x = 1 up to 8.
#
########################################################################################################################
#
#
#  SECTION V. Documentation for the code.
#
#  1. Imports needed: 
#     
#     (i). requests (to website access)
#     (ii). BeautifulSoup, SoupStrainer for the reading of the HTML webpages content
#     (iii). csv to generate the desired .csv file
#     (iv). sqlite3 to create the data base and table in the data base
#
#  2. Variables:
#
#      main_link0 (string) - link containing the CORE of the link showing the boats' info contents in batches of hundreds
#      website_link (string) - actual website of Boat Trader (R)
#      boatsdata_file (sting) - variable related with the name of csv file containing the info
#      x (integer) - variable controling the number of page containing baches of 100 boats
#      aux_link (sting) - portion of the link that controls the page number we are visiting
#      main_link (sting) - ACTUAL link showing the info of hundred boats
#      r (string) - contains the response obtained when accessing main_link website
#      ad_page_html (string) - contains the html page info associated with main_link
#      soup (string) - Formatted html page info obtained from the soup of ad_page_html
#      boat_price (array) - Array of length 100 containing the prices of the 100 boats displayed by main_link
#      MoreInfo_button (array) - Array of lentgh 100 containing the links of the "more info" button
#      k (integer) - Integer allowing to loop over all the "More Info" buttons in a fixed page
#      inside_link (string) - "Piece" of link (href) that helps getting the phone number, make and model of a boat
#                             The name "inside" can be understood as we have "clicked" the More Info button in a boat
#      t (string) - contains the response obtained when accessing inside_link website
#      inside_ad_page_html (string) - contains the html page info associated with inside_link
#      inside_soup (string) - Formatted html page info obtained from the soup of inside_ad_page_html
#      boat_phone (string) - contains the phone number of the boat's seller in question
#      NumBoat (integer) - number of datum in file
#      model_db (string) - variable storing the model of the boat to write to the table in the data base
#      phone_db (string) - variable storing the phone number to write to the table in the data base
#      price_db (string) - variable storing the price of the boat to write to the table in the data base
#
########################################################################################################################
#
#
#  SECTION VI. Actual code
#
#
# Import the requests library to access the website
import requests
# Import BeautifulSoup to get the info from the website
#from bs4 import BeautifulSoup, SoupStrainer
from bs4 import BeautifulSoup, SoupStrainer
###
###
# Import csv package to generate the CSV file 
import csv as csv
#
#
### Import sqlite3 package for the handling of the data base
import sqlite3
#
## Create an empty data base named DBBoats
#
#db = sqlite3.connect('DataB/RoyDB')
db = sqlite3.connect('DBBoats')
#
# ... as well as its corresponding cursor
#
cursor = db.cursor()
#
# Create the desired categories in the table (named boats) within the data base
#
cursor.execute('''
    CREATE TABLE boats(id INTEGER PRIMARY KEY unique, model_make TEXT,
                       phone_num TEXT, price TEXT)
''')
#
#
# This variable controls the "core" of the link allowing displaying the boats info in batches of desired sizes, in our
# case in hundreds
main_link0="http://www.boattrader.com/search-results/NewOrUsed-used/Type-Sail/Category-all/Region-all/Sort-Length:DESC"
#
# This variable strores the "core" of the link displaying the phone number of the boat found by "main_link0"
website_link = "http://www.boattrader.com"
#
# We open the BoatData.csv file where we will WRITE (=wb) the boats' info
# We also create the corresponding object associted with the file
boatsdata_file = open("BoatsData.csv", "wb")
boatsdata_file_object = csv.writer(boatsdata_file)
# 
# We write to file the legends "Number of Boat in list", "Model","Phone Number","Price"
boatsdata_file_object.writerow(["Number of Boat in list","Year","Model","Area Code","Phone Number","Price"])
##            
# We now start the process of visiting the first 8 website, each containing 100 boats' info.
# x is the integer that will control the scanning through of the websites.
#             (0,8)
for x in range(26,100):
    # We store the portion of the link the controls the page number we are visiting, which in turn is controled
    # by x. This portion is stored in aux_link
    # x is turned into a string x --> str(x) so that we can add it as such and get the desired link
    #
    aux_link = "/Page-" + str(x+1) + ",100"
    # 
    # Obtain the ACTUAL link showing the hunderd boats of the corrsponding xth page
    main_link = main_link0 + aux_link
    #
    # Get the response of main_link
    #
    r = requests.get(main_link)
    #
    # Get the HTML page info associated with main_link
    #
    ad_page_html = r.text
    #
    # Make the HTML soup associated with main_link and format it using BeautifulSoup
    soup = BeautifulSoup(ad_page_html, 'html.parser')
    ##
    ## Get the price of ALL the boats obtained by accessing main_link
    boat_price = soup.find_all('div',{'class':'ad-price'})
    ##
    ## Get the links of ALL the more info buttons, which will lead to model, make and phone numbers
    MoreInfo_button = soup.find_all('a',{'class':'btn btn-orange'})
    #
    # For a FIXED website containing hundred boats (controled by main_link)
    # we acess EACH of the hundred "More Info" buttons to get model, make and phone number 
    # of EACH boat. This is controlled by k
    for k in range(0,100):
        # 
        #  We determine the ACTUAL link containing the phone number, model and make of the kth boat
        #  displayed in main_link. This is stored in inside_link
        #  Notice how .get('href') gets the actual link "portion" needed
        #
        inside_link = website_link + MoreInfo_button[k].get('href')
        #
        # We request the response of inside_link
        #
        t = requests.get(inside_link)
        ##
        ## Get the HTML page info associated with inside_link
        ##
        inside_ad_page_html = t.text
        ##
        ## Make the soup from the link inside_link
        #
        inside_soup = BeautifulSoup(t.text, 'html.parser')
        #
        # Get the phone number "location" within the HTML content of current boat..
        # NOTE. Keep in mind the current phone number is the mirror inversion of the actual phone number
        #
        boat_phone = inside_soup.find_all('div',{'class':'phone'})
        #
        # ...and from it get the ACTUAL phone number 
        # 
        phone_num = boat_phone[0].text
        #
        # Then replace the left parenthesis "(" of the phone number with a blank...
        #
        phone_num = phone_num.replace('(','')
        #
        # ...then do the same for the right parenthesis ")" ...
        #
        phone_num = phone_num.replace(')','')
        #
        # ... and finally mirror-invert the phone number
        #
        phone_num = phone_num[::-1]
        #
        #
        # We determine the number of datum in file
        #
        NumBoat = k + 1 + (x*100)
        #
        #
        # Copy the model, phone and price to model_db, phone_db and price_db, respectively.
        # The three latter variables will be used to write data to our data base and csv file
        #
        model_db = MoreInfo_button[k].get('title')
        #
        phone_db = phone_num[0:11]
        #
        price_db = boat_price[k].text[22:37]
        #
        # Print the data to the csv file. 
        # Notes:
        #
        # a. The model and make of the kth boat is obtained by .get('title'),
        #    that is: MoreInfo_button[k].get('title')
        # b. The phone_num string is cut to [0:11] in order to get a concise short string
        # c. The actual boat_price[k] is gotten by .text and is cut in order to get a concise short string
        #
        boatsdata_file_object.writerow([NumBoat,model_db[0:4],model_db,phone_num[0:3],phone_db,price_db])
        #
        #
        # Write data to the basis set previously created
        # 
        # 
        cursor.execute('''INSERT INTO boats(model_make,phone_num, price)
                  VALUES(?,?,?)''', (model_db,phone_db,price_db))
        #
        #
        # The following line is added to print the same data to screen
        #
        print NumBoat,model_db[0:4],model_db,phone_num[0:3],phone_db,price_db
        #
        #
#
# 
# We close the csv file...
# 
boatsdata_file.close()
#
# Commit the data in the data base
#
db.commit()
#
# The next three instructions are added to check the data have been properly written to the data base 
#
testDB = cursor.execute('''select * from boats''')
#
# and we check the data extracted are the desired ones...
#
for row in testDB:
    print row
#
# ... and print 'Done' to screen to letting us know the code is finished
#
print 'Done'
#
#
