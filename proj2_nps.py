## proj_nps.py
## Skeleton for Project 2, Winter 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import *
import plotly.plotly as py
import requests
import json
from bs4 import BeautifulSoup

########## Part 1 ###########################################################################################
#Cache for part 1
CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

def get_unique_key(url):
  return url

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NationalSite():
    # needs to be changed, obvi.
    address_street = '1'
    address_city = '2'
    address_state = '3'
    address_zip = '4'

    def __init__(self, type, name, desc=None, url=None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url


    def __str__(self):
        statement = self.name + " (" + self.type + "): "
        statement += self.address_street + ", "+ self.address_city + ", "+self.address_state + " "+self.address_zip
        return statement

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov

def get_sites_for_state(state_abbr):

    url = 'https://www.nps.gov/state/'
    url_state = url + state_abbr + '/index.htm'
    page_text = make_request_using_cache(url_state)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    # Find name,type,description
    parks_list = []
    park_div = page_soup.find_all(class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    for i in range(len(park_div)):
        #h3+a name,h2 type, p description
        name = park_div[i].find('a').string
        type = park_div[i].find('h2').string
        description = park_div[i].find('p').string
        park_url = park_div[i].find('a')['href']
        park_url = "https://www.nps.gov/" + park_url + "/index.htm"
        park_page_text = make_request_using_cache(park_url)
        park_page_soup = BeautifulSoup(park_page_text, 'html.parser')

        #span itemprop,addressLocality,addressRegion,postalCode,streetAddress
        street = park_page_soup.find(attrs={"itemprop" : "streetAddress"}).string
        street = str(street)
        street = street[1:-1]
        city = park_page_soup.find(attrs={"itemprop" : "addressLocality"}).string
        state = park_page_soup.find(class_='region').string
        postcode = park_page_soup.find(attrs={"itemprop" : "postalCode"}).string
        postcode = str(postcode)
        postcode = postcode[0:5]
        park = NationalSite(type=type, name=name, desc=description)
        park.address_street=street
        park.address_city=city
        park.address_state=state
        park.address_zip=postcode
        parks_list.append(park)

    return parks_list


######### Part 2 #################################################################################################
# API cache
CACHE_FNAME = 'cache_file_name.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)


def make_API_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)


    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]


    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name,lat,lng):
        self.name = name
        self.lat =lat
        self.lng =lng

    def __str__(self):
        #a __str__( ) method, which simply prints the Place name.
        print(self.name)

## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    # get the GPS coordinates for a site
    baseurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {}
    params['key'] = google_places_key
    params['query'] = national_site.name + " " + national_site.type
    nearbyplace = make_API_request_using_cache(baseurl, params)
    nearbyplace_list = []
    if nearbyplace != []:
        lat = str(nearbyplace[0]['geometry']['location']['lat'])
        lng = str(nearbyplace[0]['geometry']['location']['lng'])
        #get the nearby places
        name_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {}
        params['location'] = lat + ","+lng
        params['radius'] = 10000
        params['key'] = google_places_key
        place_name = make_API_request_using_cache(name_url, params)['results']

        if place_name != []:
            for i in range(len(place_name)):
                name = place_name[i]['name']
                lat = str(place_name[i]['geometry']['location']['lat'])
                lng = str(place_name[i]['geometry']['location']['lng'])
                nearby_place = NearbyPlace(name = name,lat = lat,lng = lng)
                nearbyplace_list.append(nearby_place)
    return nearbyplace_list


## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    park_list = get_sites_for_state(state_abbr)
    lat_vals = []
    lon_vals = []
    text_vals = []
    #find GPS coordinates for(park list[i])
    for i in range(len(park_list)):
        baseurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        params = {}
        params['key'] = google_places_key
        params['query'] = park_list[i].name + " " + park_list[i].type
        nearbyplace = make_API_request_using_cache(baseurl, params)['results']
        if len(nearbyplace) != 0 and park_list[i].name !=None:
            lat = nearbyplace[0]['geometry']['location']['lat']
            lng = nearbyplace[0]['geometry']['location']['lng']
            lat_vals.append(lat)
            lon_vals.append(lng)
            text_vals.append(park_list[i].name)

    # plotly
    data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'star',
        ))]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
            title = 'NationalSites',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )

    fig = dict(data=data, layout=layout )
    py.plot(fig, validate=False)


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    nearbyplace_list = get_nearby_places_for_site(site_object)
    lat_vals = []
    lon_vals = []
    text_vals = []
    site_lat_vals = []
    site_lon_vals = []
    site_text_vals = []
    for i in range(len(nearbyplace_list)):
        if len(nearbyplace_list) != 0:
            if nearbyplace_list[i].name != site_object.name:
                lat_vals.append(nearbyplace_list[i].lat)
                lon_vals.append(nearbyplace_list[i].lng)
                text_vals.append(nearbyplace_list[i].name)
            else:
                site_lat_vals.append(nearbyplace_list[i].lat)
                site_lon_vals.append(nearbyplace_list[i].lng)
                site_text_vals.append(nearbyplace_list[i].name)


    site = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = site_lon_vals,
            lat = site_lat_vals,
            text = site_text_vals,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = 'red'
            ))
    nearby = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'circle',
                color = 'blue'
            ))

    data = [site, nearby]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    lat_vals = lat_vals + site_lat_vals
    lon_vals = lon_vals + site_lon_vals
    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
            title = 'National Site Nearby Places',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center = {'lat': center_lat, 'lon': center_lon },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )


    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False )

####Part 4 ##############################################################################
def get_input ():
    # input
    command = input("Enter command (or 'help' for options): ")
    command_list = command.split()
    if (command_list[0] not in ['list','nearby','help','exit','map']):
        print("invalid command! Try it again,should be the correct commands.")
    return command_list

def interactive ():
    instruction = '''
    list <stateabbr>
        available anytime
        lists all National Sites in a state
        valid inputs: a two-letter state abbreviation
    nearby <result_number>
        available only if there is an active result set
        lists all Places nearby a given result
        valid inputs: an integer 1-len(result_set_size)
    map
        available only if there is an active result set
        displays the current results on a map
    exit
        exits the program
    help
        lists available commands (these instructions)
    '''
    print(instruction)
    command_list=get_input ()

    while command_list[0]!= "exit":
        # help
        if command_list[0]== "help":
            print(instruction)
            command_list=get_input ()

        if command_list[0]== "list":
            if command_list[1].isalpha() is True:
                search_word ="National Sites in "+command_list[1] + '''
                '''
                print(search_word)
                park_list =[]
                park_list = get_sites_for_state(command_list[1])
                if len(park_list) != 0:
                    for i in range(len(park_list)):
                        park = park_list[i].__str__()
                        print (i+1,park)

                    # nearby
                    command_list=get_input ()
                    if park_list != [] and command_list[0]== "nearby":
                        if command_list[1].isdigit() is True:
                            if int(command_list[1]) <= len(park_list) and int(command_list[1]) >=1:
                                number =int(command_list[1])-1
                                name = park_list[number].name
                                sitetype = park_list[number].type
                                site = NationalSite(type= sitetype,name=name)
                                nearyby_places = get_nearby_places_for_site(site)
                                for i in nearyby_places:
                                    print (i+1,i.name)
                                command_list=get_input ()
                                # map
                                if nearyby_places != [] and command_list[0]== "map":
                                    plot_nearby_for_site(site)
                                else:
                                    print("invalid input!")
                                    command_list=get_input ()
                            else:
                                print("invalid input! Try it again,should be a an integer 1-len(result_set_size).")
                                command_list=get_input ()
                        else:
                            print("invalid input! Try it again,should be a an integer 1-len(result_set_size).")
                            command_list=get_input ()
                    else:
                        print("invalid input!")
                        command_list=get_input ()

            else:
                print("invalid input! Try it again,should be a two-letter state abbreviation.")
                command_list=get_input ()

        if command_list[0]== "exit":
            exit()

interactive()
