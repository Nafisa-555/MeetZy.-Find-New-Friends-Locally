import math
from typing import List, Optional


def calculate_match_percentage(
    user_interests: List[int],
    candidate_interests: List[int]
) -> int:
    """
    Calculate match percentage between two users based on common interests.
    
    Algorithm:
    - Converts interest lists to sets
    - Finds intersection (common interests)
    - Calculates percentage: (common / total_user_interests) * 100
    - Returns integer percentage (0-100)
    
    Args:
        user_interests: List of interest IDs for first user
        candidate_interests: List of interest IDs for second user
    
    Returns:
        Integer percentage between 0 and 100
    """
    # Handle edge case where user has no interests
    if not user_interests:
        return 0
    
    # Convert to sets and find common interests
    user_set = set(user_interests)
    candidate_set = set(candidate_interests)
    common_interests = user_set.intersection(candidate_set)
    
    # Calculate percentage
    match_percentage = int((len(common_interests) / len(user_set)) * 100)
    
    return match_percentage


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> Optional[float]:
    """
    Calculate distance between two geographic points using Haversine formula.
    
    Algorithm:
    - Converts latitude and longitude from degrees to radians
    - Uses Haversine formula to calculate great-circle distance
    - Returns distance in kilometers
    - Handles None values by returning None
    
    Args:
        lat1: Latitude of first point (degrees, -90 to 90)
        lon1: Longitude of first point (degrees, -180 to 180)
        lat2: Latitude of second point (degrees, -90 to 90)
        lon2: Longitude of second point (degrees, -180 to 180)
    
    Returns:
        Distance in kilometers, or None if any coordinate is None
    """
    # Handle None values
    if any(coord is None for coord in [lat1, lon1, lat2, lon2]):
        return None
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Calculate distance
    distance = R * c
    
    return distance


def get_common_interests(
    user_interests: List[int],
    candidate_interests: List[int]
) -> List[int]:
    """
    Find common interests between two users.
    
    Args:
        user_interests: List of interest IDs for first user
        candidate_interests: List of interest IDs for second user
    
    Returns:
        List of common interest IDs
    """
    user_set = set(user_interests)
    candidate_set = set(candidate_interests)
    common = user_set.intersection(candidate_set)
    
    return list(common)
