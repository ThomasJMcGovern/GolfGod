"""
Weather data collector using free APIs (NOAA or Open-Meteo).
Collects historical weather for tournament locations.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class WeatherCollector:
    """Collect historical weather data for golf tournaments."""
    
    # Open-Meteo API (free, no key required)
    OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    def __init__(self):
        """Initialize weather collector."""
        self.session = requests.Session()
        
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """
        Get latitude/longitude for a location.
        
        Args:
            location: City or course name
            
        Returns:
            Tuple of (latitude, longitude)
        """
        # Simplified geocoding - in production would use proper API
        # For now, return common golf course locations
        locations = {
            'Augusta': (33.5031, -82.0203),
            'Pebble Beach': (36.5686, -121.9495),
            'St Andrews': (56.3398, -2.7967),
            'TPC Sawgrass': (30.1975, -81.3947),
            'Torrey Pines': (32.9011, -117.2521),
        }
        
        # Default to Augusta if not found
        return locations.get(location, (33.5031, -82.0203))
    
    def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get historical weather data from Open-Meteo.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with weather data
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date,
            'end_date': end_date,
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'precipitation_sum',
                'windspeed_10m_max',
                'winddirection_10m_dominant'
            ],
            'timezone': 'America/New_York'
        }
        
        try:
            response = self.session.get(self.OPEN_METEO_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return {}
    
    def get_tournament_weather(
        self,
        location: str,
        tournament_date: str,
        days_before: int = 0,
        days_after: int = 4
    ) -> Dict:
        """
        Get weather for a tournament period.
        
        Args:
            location: Tournament location
            tournament_date: Start date of tournament
            days_before: Days before tournament to include
            days_after: Days after start to include (usually 4 for golf)
            
        Returns:
            Weather data for tournament period
        """
        # Parse date
        date = datetime.strptime(tournament_date, '%Y-%m-%d')
        start = date - timedelta(days=days_before)
        end = date + timedelta(days=days_after)
        
        # Get coordinates
        lat, lon = self.get_coordinates(location)
        
        # Fetch weather
        weather_data = self.get_historical_weather(
            lat, lon,
            start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d')
        )
        
        # Process and structure the data
        if weather_data and 'daily' in weather_data:
            processed = {
                'location': location,
                'coordinates': {'lat': lat, 'lon': lon},
                'tournament_date': tournament_date,
                'weather_days': []
            }
            
            daily = weather_data['daily']
            for i in range(len(daily['time'])):
                processed['weather_days'].append({
                    'date': daily['time'][i],
                    'temp_max_f': self._celsius_to_fahrenheit(daily['temperature_2m_max'][i]),
                    'temp_min_f': self._celsius_to_fahrenheit(daily['temperature_2m_min'][i]),
                    'wind_mph': self._kmh_to_mph(daily['windspeed_10m_max'][i]),
                    'wind_direction': daily['winddirection_10m_dominant'][i],
                    'precipitation_mm': daily['precipitation_sum'][i]
                })
            
            return processed
        
        return {}
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        if celsius is None:
            return None
        return (celsius * 9/5) + 32
    
    def _kmh_to_mph(self, kmh: float) -> float:
        """Convert km/h to mph."""
        if kmh is None:
            return None
        return kmh * 0.621371
    
    def analyze_weather_conditions(self, weather_data: Dict) -> Dict:
        """
        Analyze weather conditions for betting insights.
        
        Args:
            weather_data: Weather data from get_tournament_weather
            
        Returns:
            Analysis with wind category, difficulty score, etc.
        """
        if not weather_data or 'weather_days' not in weather_data:
            return {}
        
        # Calculate averages for tournament days (typically days 1-4)
        tournament_days = weather_data['weather_days'][0:4]
        
        avg_wind = sum(d['wind_mph'] for d in tournament_days) / len(tournament_days)
        max_wind = max(d['wind_mph'] for d in tournament_days)
        total_precip = sum(d['precipitation_mm'] for d in tournament_days)
        
        # Categorize conditions
        wind_category = 'calm'
        if avg_wind > 15:
            wind_category = 'windy'
        elif avg_wind > 20:
            wind_category = 'very_windy'
        
        difficulty_score = 0
        if avg_wind > 15:
            difficulty_score += 2
        if max_wind > 25:
            difficulty_score += 1
        if total_precip > 10:
            difficulty_score += 1
        
        return {
            'avg_wind_mph': round(avg_wind, 1),
            'max_wind_mph': round(max_wind, 1),
            'total_precipitation_mm': round(total_precip, 1),
            'wind_category': wind_category,
            'difficulty_score': difficulty_score,
            'conditions_summary': self._get_conditions_summary(wind_category, total_precip)
        }
    
    def _get_conditions_summary(self, wind_category: str, precipitation: float) -> str:
        """Generate human-readable conditions summary."""
        conditions = []
        
        if wind_category == 'very_windy':
            conditions.append("Very challenging wind conditions")
        elif wind_category == 'windy':
            conditions.append("Moderate wind")
        else:
            conditions.append("Calm conditions")
        
        if precipitation > 20:
            conditions.append("significant rain")
        elif precipitation > 5:
            conditions.append("some rain")
        else:
            conditions.append("dry")
        
        return ", ".join(conditions)


def main():
    """Test weather collector functionality."""
    collector = WeatherCollector()
    
    # Test with a known tournament
    print("Testing weather collection for Augusta National...")
    weather = collector.get_tournament_weather(
        location='Augusta',
        tournament_date='2024-04-11'  # 2024 Masters
    )
    
    if weather:
        print(f"Got weather for {len(weather['weather_days'])} days")
        
        # Analyze conditions
        analysis = collector.analyze_weather_conditions(weather)
        print(f"Weather Analysis: {analysis}")


if __name__ == "__main__":
    main()