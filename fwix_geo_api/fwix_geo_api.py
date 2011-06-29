"""
 * Copyright 2011 Fwix, Inc
 *
 * Permission to use, copy, modify, distribute, and sell this software
 * and its documentation for any purpose is hereby granted without fee,
 * provided that the above copyright notice appears in all copies and that
 * both that copyright notice and this permission notice appear in
 * supporting documentation, and that the name of Fwix, Inc
 * not be used in advertising or publicity
 * pertaining to distribution of the software without specific, written
 * prior permission.  Fwix, Inc makes no representations about the 
 * suitability of this software for any
 * purpose.  It is provided "as is" without express or implied warranty.
 *
 * Fwix, Inc disclaims all warranties with regard to this software, 
 * including all implied warranties of merchantability and fitness, 
 * in no event shall Fwix, Inc be liable for any special, indirect or
 * consequential damages or any damages whatsoever resulting from loss of
 * use, data or profits, whether in an action of contract, negligence or
 * other tortious action, arising out of or in connection with the use or
 * performance of this software.
 *
 *
"""


import urllib, httplib
try:
    import json
    _json_load = lambda l: json.loads(l)
except ImportError:
    try:
        import simplejson
        _json_load = lambda l: simplejson.loads(l)
    except ImportError:
        from django.utils import simplejson # GAE
        _json_load = lambda l: simplejson.loads(l)

# these can be passed as arguments for getting content by type
kCONTENT_TYPE_NEWS = 'news'
kCONTENT_TYPE_PHOTOS = 'photos'
kCONTENT_TYPE_REVIEWS = 'user_reviews'
kCONTENT_TYPE_CRITIC_REVIEWS = 'critic_reviews'
kCONTENT_TYPE_STATUS_UPDATES = 'status_updates'
kCONTENT_TYPE_EVENTS = 'events'
kCONTENT_TYPE_REAL_ESTATE = 'real_estate'
kCONTENT_TYPE_ALL = 'all'

class FwixDict(dict):
    """ Allows treatment of Content, Locations, Categories, and Place objects as dictionaries"""    

    def __setattr__(self, attr, value):
        self[attr] = value
        super(FwixDict,self).__setattr__(attr,value)

    def url_friendly(self):
        url_friendly = {}
        for key in self.keys():
            if self[key] == None:
                continue
            url_friendly[key] = self[key]
        return url_friendly


class FwixApiError(Exception):
    
    def __init__(self, message):
        super(FwixApiError,self).__init__(message)


class FwixApi(object):
    """The main API object, initialized with your api key and 
       an optional string identifying a unique user

       Most calls to the api will take some of the following:
        latitude: a float indicating latitude 
        longitude: a float indicating longitude
        page - a dictionary including the keys 'page' and 'page_size'
        range - a dictionary including the keys 'start_date' and 'end_date'
        categories - a list of dictionaries that include the key 'category_id'
        content_types - an iterable of fwix content types. For convenience,
                        these are declared as constants: eg. kCONTENT_TYPE_REVIEWS
        radius - an integer radius, in miles, within which to fetch content (default is 10)
        sort_by - I don't think this is implemented yet
        search_query - an optional search term string

       FwixDict object implementations of many of these data types are
       included in the SDK, but do not need to be used - a standard dictionary 
       that contains the indicated keys will suffice.

    """

    debugging = False
    kGET_REQUEST = 'GET'
    kPOST_REQUEST = 'POST'
    kDELETE_REQUEST = 'DELETE'
    kBASE_URL = 'http://geoapi.fwix.com'
    kBASE_DOMAIN = 'geoapi.fwix.com'
    kPLACES_PATH = '/places.json'
    kCONTENT_PATH = '/content.json'
    kLAT_KEY = 'lat'
    kLNG_KEY = 'lng'
    kLATITUDE_KEY = 'latitude'
    kLONGITUDE_KEY = 'longitude'
    kCOUNTRY_KEY = 'country'
    kPROVINCE_KEY = 'province'
    kCITY_KEY = 'city'
    kLOCALITY_KEY = 'locality'
    kPOSTAL_CODE_KEY = 'postal_code'
    kADDRESS_KEY = 'address'
    LOCATION_KEYS = (kCOUNTRY_KEY,kPROVINCE_KEY,kCITY_KEY,kLOCALITY_KEY,kPOSTAL_CODE_KEY,kADDRESS_KEY)
    kUUID_KEY = 'uuid'
    kNAME_KEY = 'name'
    kLINK_KEY = 'link'
    kCATEGORY_ID_KEY = 'category_id'
    kCATEGORY_PARENT_ID_KEY = 'parent_id'
    kCATEGORIES_KEY = 'categories'
    kPHONE_NUMBER_KEY = 'phone_number'
    kCONTENT_TYPES_KEY = 'content_types'
    kPUBLISHED_KEY = 'published_at'
    kSOURCE_KEY = 'source'
    kTITLE_KEY = 'title'
    kBODY_KEY = 'body'
    kIMAGE_KEY = 'image'
    kAUTHOR_KEY = 'author'
    kCATEGORY = 'category'
    kLOCATION = 'location'

    def __init__(self, api_key, user_id = None):
        self._api_key = api_key
        self._user_id = user_id

    def debug(self, message):
        if self.debugging:
            print message

    def get_categories(self):
        """ Returns a list of category objects"""
        url = self.kBASE_URL + '/categories.json'
        raw_categories = self._fetch_url(url)
        categories = []

        ## recursively discovers all categories
        def parse_categories(category):
            if self.kCATEGORY_ID_KEY in category:
                current_category = Category(category[self.kCATEGORY_ID_KEY],
                                            category[self.kNAME_KEY],
                                            category.get(self.kCATEGORY_PARENT_ID_KEY,None))
                categories.append(current_category)
            if self.kCATEGORIES_KEY in category:
                for sub_category in category[self.kCATEGORIES_KEY]:
                    parse_categories(sub_category)

        parse_categories(raw_categories)
        return categories 

    def get_location(self, latitude, longitude):
        """ Returns a Location object for the given latitude and longitude """
        url = self.kBASE_URL + '/location.json'
        params = {self.kLAT_KEY : latitude, self.kLNG_KEY: longitude}
        raw_location = self._fetch_url(url, params)
        #python 2.6.(< 5) bug handling
        parsed_location = {}
        for unicode_key in raw_location:
            parsed_location[str(unicode_key)] = raw_location[unicode_key]
        location = Location(**parsed_location)
        return location

    def get_place(self, uuid):
        """ Returns a place object given a UUID"""
        url = self.kBASE_URL + '/places/%s.json' % uuid
        raw_place = self._fetch_url(url)
        return self._parse_place(raw_place['place'])

    def generic_get_places(self,params):
        """ Returns a list of places from the given api parameters"""
        url = self.kBASE_URL + self.kPLACES_PATH
        raw_places = self._fetch_url(url,params)
        places = []
        for raw_place in raw_places['places']:
            places.append(self._parse_place(raw_place))
        return places
                          
    def get_places_by_lat_lng(self,
                              latitude,
                              longitude,
                              page = None,
                              radius = None,
                              categories = None):
        """ Returns a list of places near the given lat and lng"""
        params = {self.kLAT_KEY: latitude, self.kLNG_KEY: longitude}
        params.update(self._place_filters(page,radius,categories))         
        return self.generic_get_places(params)

    def get_places_by_postal_code(self, 
                                  postal_code,
                                  page = None,
                                  radius = None,
                                  categories = None):
        """ Returns a list of places near the given postal code"""
        params = {self.kPOSTAL_CODE_KEY: postal_code}
        params.update(self._place_filters(page,radius,categories))  
        return self.generic_get_places(params)

    def get_places_by_location(self,
                               location,
                               page = None,
                               radius = None,
                               categories = None):
        """Given a location object, returns associated places"""
        params = location.get_query_map()
        params.update(self._place_filters(page,radius,categories))  
        return self.generic_get_places(params)

    def update_place_given_place(self, place):
        """Given a place object, updates information about that place, and returns a boolean of 
        whether the request succeeded or not """
        params = {}
        for key in (self.kPHONE_NUMBER_KEY,
                 self.kNAME_KEY,
                 self.kLATITUDE_KEY,
                 self.kLONGITUDE_KEY):
            params[key] = place[key]
        for key in self.LOCATION_KEYS:
            params[key] = place[self.kLOCATION][key]
        
        url = self.kBASE_URL + '/places/%s.json' % place[self.kUUID_KEY]
        response = self._fetch_url(url, params, self.kPOST_REQUEST)
        return response
        
    def update_place(self, 
                     uuid, 
                     latitude = None, 
                     longitude = None, 
                     name = None, 
                     city = None, 
                     address = None, 
                     country = None, 
                     province = None, 
                     postal_code = None,  
                     phone_number = None, 
                     category = None):
        """ Updates information about a place, returns a boolean of whether the request succeeded or not"""
        params = {}
        if latitude:
            params[self.kLAT_KEY] = latitude 
        if longitude:
            params[self.kLNG_KEY] = longitude  
        if name:
            params[self.kNAME_KEY] = name
        if city:
            params[self.kCITY_KEY] = city 
        if address:
            params[self.kADDRESS_KEY] = address
        if country:
            params[self.kCOUNTRY_KEY] = country
        if province:
            params[self.kPROVINCE_KEY] = province
        if postal_code:
            params[self.kPOSTAL_CODE_KEY] = postal_code
        if phone_number:
            params[self.kPHONE_NUMBER_KEY] = phone_number
        if category:
            params[self.kCATEGORY] = category
          
        url = self.kBASE_URL + '/places/%s.json' % uuid
        response = self._fetch_url(url, params, self.kPOST_REQUEST)
        return response    

    def delete_place(self, uuid):
        """ Deletes a place, returs a boolean of whether or not the request was succesful"""
        url = '/places/%s.json' % uuid
        response = self._fetch_url(url, request_type = self.kDELETE_REQUEST)
        if response['success'] is 1:
            return True
        else:
            return False

    def generic_get_content(self, params, content_types, page, range, sort_by, search_query):
        url = self.kBASE_URL + self.kCONTENT_PATH
        if isinstance(content_types, str):
            params[self.kCONTENT_TYPES_KEY] = content_types
        else:
            params[self.kCONTENT_TYPES_KEY] = ','.join(content_types)
        params.update(self._content_filters(page,range,sort_by,search_query))
        raw_content = self._fetch_url(url,params)
        content = []
        for type_key in kCONTENT_TYPE_TO_OBJECT.keys():
            if type_key in raw_content:
                for single_content in raw_content[type_key]:
                    content.append(self._parse_content(single_content, type_key))                    
        return content

    def get_content_by_lat_lng(self,
                               latitude,
                               longitude,
                               content_types,
                               page = None,
                               range = None,
                               sort_by = None,
                               search_query = None):
        """ Returns a list of content objects based on the given criteria"""
        params = { self.kLAT_KEY: latitude, self.kLNG_KEY: longitude }
        return self.generic_get_content(params, content_types, page, range, sort_by, search_query)

    def get_content_by_postal_code(self, 
                                   postal_code,
                                   content_types,
                                   page = None,
                                   range = None,
                                   sort_by = None,
                                   search_query = None):
        """ Returns a list of content objects near a given a postal code"""
        params = { self.kPOSTAL_CODE_KEY: postal_code }
        return self.generic_get_content(params, content_types, page, range, sort_by, search_query)

    def get_content_by_location(self,
                                location,
                                content_types,
                                page = None,
                                range = None,
                                sort_by = None,
                                search_query = None):
        """ Returns a list of content objects near a given location object"""
        params = location.url_friendly()
        return self.generic_get_content(params, content_types, page, range, sort_by, search_query)

    def get_content_by_place(self,
                             place_uuid, 
                             content_types,
                             page = None,
                             range = None,
                             sort_by = None,
                             search_query = None):
        """ Returns a list of content objects associated with a given place object"""
        params = {'place_id': place_uuid}
        return self.generic_get_content(params, content_types, page, range, sort_by, search_query)

    def _fetch_url(self, base_url, query_map = {}, request_type = kGET_REQUEST):
        """ Fetches json data and returns it as a dictionary"""
        query_map['api_key'] = self._api_key
        if self._user_id:
            query_map['user_id'] = self._user_id
        if request_type == self.kPOST_REQUEST:
            query_str = ''
            post_args = urllib.urlencode(query_map)
        elif request_type == self.kGET_REQUEST or request_type == self.kDELETE_REQUEST:
            query_str = '?' + urllib.urlencode(query_map)
            post_args = None
        else:
            raise NotImplementedError, 'Only POST, GET, and DELETE are now supported'
        url = base_url + query_str
        self.debug('URL: %s \nPOST: %s' % (url,post_args))
        if request_type == self.kDELETE_REQUEST: 
            conn = httplib.HTTPConnection(self.kBASE_DOMAIN)
            conn.request(self.kDELETE_REQUEST, url)
            response = conn.getresponse()
        else:
            response = urllib.urlopen(url, post_args)
        try:
            parsed_response = _json_load(response.read())
        except Exception, e:
            self.debug(response.read())
            raise e
        finally:
            if request_type == self.kDELETE_REQUEST:
                response_code = response.status
                conn.close()
            else:
                response_code = response.getcode()
                response.close()

        if int(response_code) != 200:
            raise FwixApiError('Bad Request : ' + parsed_response['message'])
        
        return parsed_response

    def _parse_content(self, raw_content, content_type):
        """ Converts content JSON into content object"""
        new_content = {}
        new_content['type'] = content_type
        new_content[self.kLATITUDE_KEY] = raw_content.get(self.kLAT_KEY,None)
        new_content[self.kLONGITUDE_KEY] = raw_content.get(self.kLNG_KEY, None)
        for key in (self.kUUID_KEY,
                    self.kLINK_KEY, 
                    self.kPUBLISHED_KEY, 
                    self.kSOURCE_KEY, 
                    self.kTITLE_KEY, 
                    self.kBODY_KEY, 
                    self.kIMAGE_KEY,
                    self.kAUTHOR_KEY):
            new_content[key] = raw_content.get(key, None)
        for extra_key in kCONTENT_TYPE_TO_OBJECT[content_type].extra_attributes():
            new_content[extra_key] = raw_content.get(key, None)
        content = kCONTENT_TYPE_TO_OBJECT[content_type](**new_content)
        return content

    def _parse_place(self, raw_place):
        """Converts place JSON into place object"""
        new_place = {}
        new_location = {}
        categories = []
        for place_key in (self.kPHONE_NUMBER_KEY,
                     self.kUUID_KEY,
                     self.kNAME_KEY,
                     self.kLINK_KEY):
            new_place[place_key] = raw_place[place_key]
        for loc_key in self.LOCATION_KEYS:
            if loc_key in raw_place:
                new_location[loc_key] = raw_place[loc_key]
        location = Location(**new_location)
        new_place['location'] = location
        new_place[self.kLATITUDE_KEY] = raw_place[self.kLAT_KEY]
        new_place[self.kLONGITUDE_KEY] = raw_place[self.kLNG_KEY]
        for category in raw_place[self.kCATEGORIES_KEY]:
            #python 2.6.(< 5) bug handling
            parsed_category = {}
            for unicode_key in category:
                parsed_category[str(unicode_key)] = category[unicode_key]
            categories.append(Category(**parsed_category))
        new_place[self.kCATEGORIES_KEY] = categories
        place = Place(**new_place)
        return place
        
    def _place_filters(self, page, radius, categories):
        """ Returns a dictionary for use with fetching from the api based on common place inputs"""
        filters = {}
        if page:
            filters.update(page)
        if radius:
            filters['radius'] = radius
        if categories:
            for category in categories:
                filters[kCATEGORIES_KEY] += (category['category_id'] + ',')
            filters[kCATEGORIES_KEY] = filters[kCATEGORIES_KEY][:-1]
        return filters

    def _content_filters(self, page, range, sort_by, search_query):
        """ Returns a dictionary for use with fetching from the api based on common content inputs"""
        filters = {}
        if page:
            filters.update(page)
        if range:
            filters.update(range)
        if search_query:
            filters['query'] = search_query
        return filters

            
class Location(FwixDict):
    
    def __init__(self,
                country,
                province = None,
                city = None,
                locality = None,
                postal_code = None,
                address = None):
        self.country = country
        self.province = province
        self.city = city
        self.locality = locality
        self.postal_code = postal_code
        self.address = address
        super(Location, self).__init__()

    def get_query_map(self):
        query_map = {}
        for key in self.keys():
            if self[key] is not None:
                query_map[key] = self[key]
        return query_map


class Category(FwixDict):

    def __init__(self,
                category_id,
                name,
                parent_category_id = None):
        self.category_id = category_id
        self.parent_id = parent_category_id
        self.name = name
        super(Category, self).__init__()


class Place(FwixDict):
    
    def __init__(self,
                uuid,
                name,
                latitude, 
                longitude, 
                phone_number, 
                location, 
                link, 
                categories, 
                facebook_id=None, 
                twitter_id=None):
        self.uuid = uuid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude  
        self.phone_number = phone_number
        self.location = location
        self.link = link
        self.categories = categories
        self.facebook_id = facebook_id
        self.twitter_id = twitter_id
        super(Place, self).__init__()



class Content(FwixDict):

    def __init__(self,
                type,
                uuid,
                latitude,
                longitude,
                title,
                body,
                author,
                published_at,
                link,
                source,
                image):
        self.type = type
        self.uuid = uuid
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.body = body
        self.author = author
        self.published_at = published_at
        self.link = link
        self.source = source
        self.image = image
        super(Content, self).__init__()

    @classmethod
    def extra_attributes(self):
        return ()

class StatusUpdate(Content):

    def __init__(self, *args, **kwargs):
        super(StatusUpdate, self).__init__(*args, **kwargs)


class Photo(Content):

    kTHUMBNAIL = 'thumbnail'

    def __init__(self, *args, **kwargs):
        self.thumbnail = kwargs[self.kTHUMBNAIL]
        del kwargs[self.kTHUMBNAIL]
        super(Photo, self).__init__(*args, **kwargs)

    @classmethod
    def extra_attributes(self):
        return (self.kTHUMBNAIL,)


class Review(Content):

    kRATING = 'rating'

    def __init__(self, *args, **kwargs):
        self.rating = kwargs[self.kRATING]
        del kwargs[self.kRATING]
        super(Review, self).__init__(*args, **kwargs)

    @classmethod
    def extra_attributes(self):
        return (self.kRATING,)


class UserReview(Content):

    def __init__(self, *args, **kwargs):
        super(UserReview, self).__init__(*args, **kwargs)


class CriticReview(Content):

    def __init__(self, *args, **kwargs):
        super(CriticReview, self).__init__(*args, **kwargs)


class News(Content):

    def __init__(self, *args, **kwargs):
        super(News, self).__init__(*args, **kwargs)


class Event(Content):

    kLOCAL_START_TIME = 'local_start_time'
    kLOCAL_END_TIME = 'local_end_time'

    def __init__(self, *args, **kwargs):
        for attr in self.extra_attributes():
            setattr(self,attr,kwargs[attr])
            del kwargs[attr]
        super(Event, self).__init__(*args, **kwargs)

    @classmethod
    def extra_attributes(self):
        return (self.kLOCAL_START_TIME, self.kLOCAL_END_TIME)


class RealEstate(Content):

    kLOCATION = 'location'
    kPRICE = 'price'
    kNUMBER_OF_BEDS = 'number_of_beds'
    kNUMBER_OF_BATHS = 'number_of_baths'
    kSQUARE_FEET = 'square_feet'
    kPROPERTY_TYPE = 'property_type'
    
    def __init__(self, *args, **kwargs):
        for attr in self.extra_attributes():
            setattr(self,attr,kwargs[attr])
            del kwargs[attr]
        super(RealEstate, self).__init__(*args, **kwargs)

    @classmethod
    def extra_attributes(self):
        return (self.kLOCATION,
                    self.kPRICE,
                    self.kNUNBER_OF_BEDS,
                    self.kSQUARE_FEET,
                    self.kPROPERTY_TYPE)


kCONTENT_TYPE_TO_OBJECT = {
    kCONTENT_TYPE_NEWS : News,
    kCONTENT_TYPE_PHOTOS : Photo,
    kCONTENT_TYPE_REVIEWS : UserReview,
    kCONTENT_TYPE_CRITIC_REVIEWS : CriticReview,
    kCONTENT_TYPE_STATUS_UPDATES : StatusUpdate,
    kCONTENT_TYPE_EVENTS : Event,
    kCONTENT_TYPE_REAL_ESTATE : RealEstate}


class Page(FwixDict):
    """ Page is an object that indicates which page number to fetch, given a page size"""

    def __init__(self, page_number, page_size):
        self.page = page_number
        self.page_size = page_size


class Range(FwixDict):
    """ Range indicates a range between datetime objects """
    
    def __init__(self,start_date, end_date):
        """ start and end should both be datetime objects """
        self.start_date = start_date
        self.end_date = end_date

