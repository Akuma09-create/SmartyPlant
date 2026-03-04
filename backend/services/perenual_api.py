"""
Perenual Plant API Integration for Smart Plant Health Assistant.
Fetches plant details: common name, scientific name, watering, sunlight, growth cycle, images.
API Documentation: https://perenual.com/docs/api
"""

import os
import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Perenual API base URL
PERENUAL_BASE_URL = "https://perenual.com/api"


class PerenualAPI:
    """
    Client for Perenual Plant API.
    Provides plant species data, care guides, and images.
    """

    def __init__(self, api_key: str = None):
        """Initialize with API key from parameter or environment."""
        self.api_key = api_key or os.getenv('PERENUAL_API_KEY')
        self._initialized = bool(self.api_key)
        
        if self._initialized:
            logger.info("Perenual API initialized")
        else:
            logger.warning("No Perenual API key found. Set PERENUAL_API_KEY env variable.")

    @property
    def is_available(self) -> bool:
        return self._initialized

    def search_plants(self, query: str, page: int = 1) -> Optional[Dict]:
        """
        Search for plants by name.
        
        Args:
            query: Plant name to search for
            page: Page number for pagination
            
        Returns:
            Dict with search results or None on error
        """
        if not self.is_available:
            return None

        try:
            url = f"{PERENUAL_BASE_URL}/species-list"
            params = {
                'key': self.api_key,
                'q': query,
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Perenual search for '%s': found %d results", query, len(data.get('data', [])))
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Perenual API search error: %s", e)
            return None

    def get_plant_details(self, plant_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific plant.
        
        Args:
            plant_id: Perenual plant ID
            
        Returns:
            Dict with plant details or None on error
        """
        if not self.is_available:
            return None

        try:
            url = f"{PERENUAL_BASE_URL}/species/details/{plant_id}"
            params = {'key': self.api_key}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Perenual details for ID %d: %s", plant_id, data.get('common_name', 'Unknown'))
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Perenual API details error: %s", e)
            return None

    def get_care_guide(self, species_id: int) -> Optional[Dict]:
        """
        Get care guide for a plant species.
        
        Args:
            species_id: Perenual species ID
            
        Returns:
            Dict with care guide or None on error
        """
        if not self.is_available:
            return None

        try:
            url = f"{PERENUAL_BASE_URL}/species-care-guide-list"
            params = {
                'key': self.api_key,
                'species_id': species_id
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Perenual API care guide error: %s", e)
            return None

    def search_and_get_details(self, plant_name: str) -> Optional[Dict]:
        """
        Search for a plant by name and return formatted details.
        
        Args:
            plant_name: Common or scientific name of the plant
            
        Returns:
            Formatted plant info dict or None
        """
        if not self.is_available:
            return None

        # Search for the plant
        search_result = self.search_plants(plant_name)
        if not search_result or not search_result.get('data'):
            logger.warning("No plants found for '%s'", plant_name)
            return None

        # Get the first match
        first_match = search_result['data'][0]
        plant_id = first_match.get('id')
        
        if not plant_id:
            return self._format_basic_info(first_match)

        # Get detailed info
        details = self.get_plant_details(plant_id)
        if details:
            return self._format_detailed_info(details)
        
        return self._format_basic_info(first_match)

    def _format_basic_info(self, data: Dict) -> Dict:
        """Format basic plant info from search results."""
        # Handle watering - can be string or dict
        watering = data.get('watering', 'Unknown')
        if isinstance(watering, dict):
            watering = watering.get('value', 'Unknown')
            
        # Handle sunlight - can be list or string
        sunlight = data.get('sunlight', [])
        if isinstance(sunlight, list):
            sunlight_str = ', '.join(sunlight) if sunlight else 'Unknown'
        else:
            sunlight_str = str(sunlight)

        return {
            'source': 'perenual',
            'id': data.get('id'),
            'common_name': data.get('common_name', 'Unknown'),
            'scientific_name': self._get_scientific_name(data),
            'family': data.get('family', 'Unknown'),
            'plant_type': data.get('type', 'Unknown'),
            'cycle': data.get('cycle', 'Unknown'),
            'watering': watering,
            'sunlight': sunlight_str,
            'sunlight_list': sunlight if isinstance(sunlight, list) else [sunlight],
            'description': data.get('description', ''),
            'images': self._extract_images(data),
            'default_image': self._get_default_image(data),
        }

    def _format_detailed_info(self, data: Dict) -> Dict:
        """Format detailed plant info."""
        basic = self._format_basic_info(data)
        
        # Add detailed fields
        basic.update({
            'origin': self._safe_join(data.get('origin', [])),
            'dimension': data.get('dimension', 'Unknown'),
            'dimensions': data.get('dimensions', {}),
            'propagation': self._safe_join(data.get('propagation', [])),
            'hardiness': data.get('hardiness', {}),
            'hardiness_zone': self._get_hardiness_zone(data),
            'watering_general_benchmark': data.get('watering_general_benchmark', {}),
            'growth_rate': data.get('growth_rate', 'Unknown'),
            'maintenance': data.get('maintenance', 'Unknown'),
            'care_level': data.get('care_level', 'Unknown'),
            'drought_tolerant': data.get('drought_tolerant', False),
            'salt_tolerant': data.get('salt_tolerant', False),
            'thorny': data.get('thorny', False),
            'invasive': data.get('invasive', False),
            'tropical': data.get('tropical', False),
            'indoor': data.get('indoor', False),
            'flowers': data.get('flowers', False),
            'flower_color': data.get('flower_color', ''),
            'flowering_season': data.get('flowering_season', ''),
            'leaf': data.get('leaf', False),
            'leaf_color': self._safe_join(data.get('leaf_color', [])),
            'edible_leaf': data.get('edible_leaf', False),
            'edible_fruit': data.get('edible_fruit', False),
            'fruiting_season': data.get('fruiting_season', ''),
            'cuisine': data.get('cuisine', False),
            'medicinal': data.get('medicinal', False),
            'poisonous_to_humans': data.get('poisonous_to_humans', 0),
            'poisonous_to_pets': data.get('poisonous_to_pets', 0),
            'attracts': self._safe_join(data.get('attracts', [])),
            'pest_susceptibility': self._safe_join(data.get('pest_susceptibility', [])),
            'pruning_month': self._safe_join(data.get('pruning_month', [])),
            'soil': self._safe_join(data.get('soil', [])),
            'care_guides': data.get('care-guides', ''),
        })
        
        return basic

    def _get_scientific_name(self, data: Dict) -> str:
        """Extract scientific name from data."""
        sci_name = data.get('scientific_name', [])
        if isinstance(sci_name, list):
            return sci_name[0] if sci_name else 'Unknown'
        return str(sci_name) if sci_name else 'Unknown'

    def _safe_join(self, items) -> str:
        """Safely join list items into a string."""
        if isinstance(items, list):
            return ', '.join(str(i) for i in items if i) if items else 'Unknown'
        return str(items) if items else 'Unknown'

    def _get_hardiness_zone(self, data: Dict) -> str:
        """Extract hardiness zone range."""
        hardiness = data.get('hardiness', {})
        if isinstance(hardiness, dict):
            min_zone = hardiness.get('min', '')
            max_zone = hardiness.get('max', '')
            if min_zone and max_zone:
                return f"{min_zone} - {max_zone}"
            return str(min_zone or max_zone or 'Unknown')
        return 'Unknown'

    def _extract_images(self, data: Dict) -> List[str]:
        """Extract all available image URLs."""
        images = []
        
        # Default image
        default_img = data.get('default_image', {})
        if isinstance(default_img, dict):
            for key in ['original_url', 'regular_url', 'medium_url', 'small_url', 'thumbnail']:
                url = default_img.get(key)
                if url and url not in images:
                    images.append(url)
        
        return images

    def _get_default_image(self, data: Dict) -> str:
        """Get the best available default image URL."""
        default_img = data.get('default_image', {})
        if isinstance(default_img, dict):
            # Prefer medium or regular size
            for key in ['medium_url', 'regular_url', 'original_url', 'small_url', 'thumbnail']:
                url = default_img.get(key)
                if url:
                    return url
        return ''


# Singleton instance
_perenual_api = None


def get_perenual_api() -> PerenualAPI:
    """Get or create singleton Perenual API instance."""
    global _perenual_api
    if _perenual_api is None:
        _perenual_api = PerenualAPI()
    return _perenual_api
