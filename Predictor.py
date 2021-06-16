## Tennis Predictor by eyesofDaveed
## Date: 04/09/2020
## Scope.txt explains the main scope of the script


from bs4 import BeautifulSoup as BS
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import re
import sys
from matplotlib import pyplot as plt
import time
from statistics import mean
import numpy as np

# Return the first char in a string
def retractor(word):
    try:
        return int(item)
    except ValueError:
        return

# Find the total of matches and return the count
# Return 0 if None
def matchcountcheck(body):
    for item in body.splitlines():
        if "matches:" in item:
            return int(item.split(sep=": ")[1])

    return 0

# Find the best fit from 2 sets of data
def best_fit_slope(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs  * ys)) /
         ((mean(xs) * mean(xs)) - mean(xs * xs)))
    return m, b

if __name__ == '__main__':

    # Initialize the Chrome browser using webdriver library
    browser = webdriver.Chrome(ChromeDriverManager().install())

    # Access the webpage with the url and get the input for a player
    browser.get('https://www.tennisprediction.com/index.php/')
    print("---------------Welcome to the TennisPredictor!---------------")
    player = input("Type full name of the player(Last+First):")
    linklocator = player.split(sep='+')
    selectedplayer = linklocator[0] + " " + linklocator[1]

    # Locate the search form with player's input and paste the player's name and press RETURN button
    searchform = browser.find_element_by_xpath("//input[@name='player']")  # Find the search box
    searchform.send_keys(player + Keys.RETURN)

    # New web page was requested with the player's name
    # Locate the player's name on the list of results and get a link for the player's profile
    playerpage = browser.find_element_by_partial_link_text(selectedplayer)
    profilelink = playerpage.get_attribute('href')

    # Open up a browser with the link obtained for the player's profile
    browser.get(profilelink)

    # Uncheck box for 'qualifications'
    browser.find_element_by_xpath("//input[@name='tq2']").click()
    # Check box to show last 50 games
    browser.find_element_by_xpath("//input[@value='50']").click()
    # Click on the submit button with options selected above

    browser.implicitly_wait(5)
    browser.find_element_by_xpath("//input[@class='form1']").click()

    time.sleep(5)
    # Parse the web page into html text
    soup = BS(browser.page_source, "html.parser")

    # Check for the requirements, total count of games should be at least 50
    # If selected player doesn't have 50 matches, quit and notify with the error
    if matchcountcheck(soup.text) < 30:
        browser.quit()
        print("Error: selected player doesn't meet the criteria!")
        sys.exit()
    else:
    # If criteria met, retrieve all match data and store for the selected player
        data = soup.text

    # set of data to be exported
    firstsetlist = []
    secondsetlist = []
    odds = []

    # split data into lines and store them in a list
    lines = data.splitlines()
    lines = list(enumerate(lines))

    # Index of the result for the First match
    lastindex1 = 0
    # Index of the result for the Second match
    lastindex2 = 0
    # Index of the result for the Odd after 'W'
    lastindex3 = 0
    # Index of the result for the Odd when lost
    lastindex4 = 0
    # Index to track retired matches
    retindex = 0

    temp = 0
    for index, element in enumerate(lines):
        if str(selectedplayer) in str(element):
            lastindex1 = index + 2
            lastindex2 = index + 3
            lastindex4 = index + 7
            continue
        elif index == lastindex1:
            if element[1]:
                temp = element[1]
            continue
        elif index == lastindex2:
            if element[1]:
                firstsetlist.append(temp)
                secondsetlist.append(element[1])
            else:
                lastindex4 = index + 6
                lastindex3 = index + 6
            continue
        elif 'W' in str(element) and lastindex3 < index:
            lastindex3 = index + 1
            continue
        elif index == lastindex3:
            try:
                odd = float(element[1])
                if odd != 0.0:
                    odds.append(float(element[1]))
            except ValueError:
                continue
        elif index == lastindex4:
            try:
                odd = float(element[1])
                if odd != 0.0:
                    odds.append(float(element[1]))
            except ValueError:
                continue

    # Results of two set to be exported into graph
    export1 = []
    export2 = []
    firstsetlist.pop(0)
    secondsetlist.pop(0)
    odds.pop(0)

    # Retract the match results from the list and append it to the export lists
    for item in firstsetlist:
        export1.append(retractor(item))

    for item in secondsetlist:
        export2.append(retractor(item))

    # Create numpy array for the list of match results
    xs1 = np.array(export1, dtype=np.float64)
    xs2 = np.array(export2, dtype=np.float64)
    ys = np.array(odds, dtype=np.float64)


    # Find the best fit line for sets
    n, a = best_fit_slope(xs1, ys)

    regression_line_1 = []
    for x in xs1:
        regression_line_1.append((n*x)+a)

    m, b = best_fit_slope(xs2, ys)

    regression_line_2 = []
    for x in xs2:
        regression_line_2.append((m*x)+b)

    # Plot the graph for first 2 sets of the selected player
    # Graph a line sets played vs odds
    plt.plot(xs1, regression_line_1, label = "First set")
    plt.plot(xs2, regression_line_2, label = "Second set")
    plt.xlabel('# of sets')
    plt.ylabel('bk odds')
    plt.title('Average best fit line for first 2 sets')
    plt.legend()
    plt.show()

    # quit the browser
    browser.quit()