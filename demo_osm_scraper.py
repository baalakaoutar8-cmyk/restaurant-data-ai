#!/usr/bin/env python3
"""
Demonstration: OpenStreetMap Scraper - End-to-End Test
========================================================

This test demonstrates the complete workflow:
1. Load cities from configuration (Morocco)
2. Geocode city name to OpenStreetMap area ID using Nominatim
3. Generate Overpass QL query for restaurants in that area
4. Query Overpass API (VK Maps instance)
5. Parse and display results
"""

from scraping.openstreetmap.scraper import OpenStreetMapScraper

def main():
    print("\n" + "="*70)
    print("OpenStreetMap Scraper - End-to-End Demonstration")
    print("="*70 + "\n")
    
    try:
        # Initialize scraper
        scraper = OpenStreetMapScraper(country='Morocco', priority=1)
        cities = scraper.load_cities()
        
        if not cities:
            print("FAILED: No cities found")
            return
        
        # Test with first city
        city = cities[0]
        print(f"Testing with: {city['city']}, {city['country']}\n")
        
        # Step 1: Geocode city
        print(f"Step 1 - Geocoding...")
        city_info = scraper.nominatim.get_city_information(city['city'], city['country'])
        if not city_info:
            print("FAILED: Failed to geocode city")
            return
        
        print(f"  OK Latitude: {city_info['latitude']}, Longitude: {city_info['longitude']}")
        print(f"  OK Area ID: {city_info['area_id']}")
        print(f"  OK OSM Type: {city_info['osm_type']}")
        print(f"  OK OSM ID: {city_info['osm_id']}")
        
        # Step 2: Generate query
        print(f"\nStep 2 - Generating Overpass QL query...")
        query = scraper.builder.restaurants_query(city_info['area_id'])
        print(f"  OK Query generated: {len(query)} characters")
        
        # Step 3: Query Overpass
        print(f"\nStep 3 - Querying Overpass API...")
        elements = scraper.overpass.get_elements(query)
        print(f"  OK Results received: {len(elements)} restaurants/bars/cafes found")
        
        # Step 4: Display sample results
        if elements:
            print(f"\nStep 4 - Sample Results (first 5):\n")
            for i, elem in enumerate(elements[:5], 1):
                name = elem.get('tags', {}).get('name', 'Unknown')
                amenity = elem.get('tags', {}).get('amenity', 'unknown')
                cuisine = elem.get('tags', {}).get('cuisine', '-')
                print(f"  {i}. {name}")
                print(f"     Amenity: {amenity} | Cuisine: {cuisine}")
                coords = f"{elem.get('lat', 'N/A')}, {elem.get('lon', 'N/A')}"
                print(f"     Location: {coords}\n")
        
        print("="*70)
        print("SUCCESS: End-to-end test completed!")
        print("="*70 + "\n")
        
        scraper.close()
        
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
