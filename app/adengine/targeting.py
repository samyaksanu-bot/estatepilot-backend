def build_targeting(project):
    location = project.get("location")

    return {
        "locations": [location],
        "radius_km": 10,
        "interests": [
            "Real estate",
            "Property investment",
            "Apartment hunting",
            "Home loans"
        ],
        "age_min": 25,
        "age_max": 55
    }
