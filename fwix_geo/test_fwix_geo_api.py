import unittest
from fwix_geo_api import *

kFWIX_API_KEY = '' # your api key
kFWIX_LAT = 37.787462
kFWIX_LON = -122.399223
kRANDOM_PLACE_UUID = '304f36b-70c6-68ac-245f-11c9b17eafdfa'
kRANDOM_POSTCODE = 94117


class TestFwixSDK(unittest.TestCase):

    def setUp(self):
        self.fx_api = FwixApi(kFWIX_API_KEY)
        #self.fx_api.debugging = True

    def test_get_categories(self):
        categories = self.fx_api.get_categories()
        for category in categories:
            self.assertTrue(set(('category_id','parent_id','name')).issubset(set(category.keys())))

    def test_get_location(self):
        location = self.fx_api.get_location(kFWIX_LAT, kFWIX_LON) # Fwix's location
        self.assertTrue(location['province'] == 'CA' and location['city'] == 'San Francisco')

    def test_get_place(self):
        place_uuid = kRANDOM_PLACE_UUID
        place = self.fx_api.get_place(place_uuid)

    def test_get_places_by_lat_lng(self):
        places = self.fx_api.get_places_by_lat_lng(kFWIX_LAT, kFWIX_LON)

    def test_get_places_by_postal_code(self):
        places = self.fx_api.get_places_by_postal_code(kRANDOM_POSTCODE)

    def test_get_places_by_location(self):
        location = self.fx_api.get_location(kFWIX_LAT, kFWIX_LON)
        places = self.fx_api.get_places_by_location(location)

    def test_get_content_by_lat_lng(self):
        for content_type in kCONTENT_TYPE_TO_OBJECT.keys():
            if content_type == kCONTENT_TYPE_REAL_ESTATE: continue
            content = self.fx_api.get_content_by_lat_lng(kFWIX_LAT,kFWIX_LON,(content_type,))

    def test_get_content_by_postal_code(self):
        for content_type in kCONTENT_TYPE_TO_OBJECT.keys():
            if content_type == kCONTENT_TYPE_REAL_ESTATE: continue
            content = self.fx_api.get_content_by_postal_code(kRANDOM_POSTCODE,(content_type,))

    def test_get_content_by_location(self):
        for content_type in kCONTENT_TYPE_TO_OBJECT.keys():
            if content_type == kCONTENT_TYPE_REAL_ESTATE: continue
            content = self.fx_api.get_content_by_location(self.fx_api.get_location(kFWIX_LAT, kFWIX_LON), content_type)

    def test_get_content_by_place(self):
        for content_type in kCONTENT_TYPE_TO_OBJECT.keys():
            if content_type == kCONTENT_TYPE_REAL_ESTATE: continue
            content = self.fx_api.get_content_by_place(kRANDOM_PLACE_UUID,content_type)

if __name__ == '__main__':
    unittest.main()