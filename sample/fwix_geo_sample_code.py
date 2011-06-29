"""
Testing fwix_geo API
"""
import sys
sys.path.append("../")
from fwix_geo_api.fwix_geo_api import *

kFWIX_API_KEY = ''
kFWIX_LAT = 37.787462
kFWIX_LON = -122.399223
kRANDOM_PLACE_UUID = '17f5fcd-3312-7a52-f551-d4e8f70dbc8a9'
kRANDOM_POSTCODE = 94117

fwix = FwixApi(kFWIX_API_KEY)

class GeoApiTest():
	"""testing fwix geo"""
	
	def get_categories():
		""" Tests get_categories"""
		return fwix.get_categories()
	
	def get_location(lat, lng):
		""" Tests get_location"""
		return fwix.get_location(lat, lng)
		
	def get_place(uuid):
		""" Tests get_place"""
		return fwix.get_place(uuid) 
		
	def get_places_by_lat_lng(lat, lng):
		""" Tests get_places_by_lat_lng"""
		return fwix.get_places_by_lat_lng(lat, lng)
		
	def get_places_by_zip(zip):
		""" Tests get_places_by_postal_code"""
		return fwix.get_places_by_postal_code(zip) 
	
	def get_places_by_loc(lat, lng):
		""" Tests get_places_by_loc  given latitude and longitude"""
		loc = fwix.get_location(lat, lng)
		return fwix.get_places_by_location(loc)
		
	def get_content_by_lat_lng(lat, lng):
		""" Tests get_content_by_lat_lng for all content types"""
		return fwix.get_content_by_lat_lng(lat,lng, kCONTENT_TYPE_ALL)
		
	def get_specific_content_by_lat_lng(content_type, lat, lng):
		""" Tests get_content_by_lat_lng for a specific content type"""
		return fwix.get_content_by_lat_lng(lat,lng,content_type)
		
	def get_content_by_zip(zip):
		""" Tests get_content_by_postal_code for all content types"""
		return fwix.get_content_by_postal_code(zip, kCONTENT_TYPE_ALL)
		
	def get_specific_content_by_zip(zip, content_type):
		""" Tests get_content_by_postal_code for a specific content type"""
		return fwix.get_content_by_postal_code(zip,content_type)
		
	def get_content_by_location(lat, lng, content_type):
		""" Tests get_content_by_location for a specific content type"""
		return fwix.get_content_by_location(fwix.get_location(lat, lng), content_type)
			
	def get_content_by_place(uuid, content_type):
		""" Tests get_content_by_place for a specific content type"""
		return fwix.get_content_by_place(uuid, content_type)
		
	if __name__ == '__main__':
		print get_location(kFWIX_LAT, kFWIX_LON)
		
		print get_categories()
		
		print get_place(kRANDOM_PLACE_UUID)
		
		print get_places_by_lat_lng(kFWIX_LAT, kFWIX_LON)
		
		print get_places_by_zip(kRANDOM_POSTCODE)
		
		print get_places_by_loc(kFWIX_LAT, kFWIX_LON)
		
		print get_content_by_lat_lng(kFWIX_LAT, kFWIX_LON)
		
		print get_specific_content_by_lat_lng(kCONTENT_TYPE_STATUS_UPDATES, kFWIX_LAT, kFWIX_LON)
	
		print get_content_by_zip(kRANDOM_POSTCODE)
		
		print get_specific_content_by_zip(kRANDOM_POSTCODE, kCONTENT_TYPE_STATUS_UPDATES)
		
		print get_content_by_location(kFWIX_LAT, kFWIX_LON, kCONTENT_TYPE_STATUS_UPDATES)
		
		print get_content_by_place(kRANDOM_PLACE_UUID, kCONTENT_TYPE_NEWS)
