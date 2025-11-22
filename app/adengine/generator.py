def generate_ad_copy(project):
    name = project.get("name")
    location = project.get("location")
    price_start = project.get("price_start")

    headline = f"{name} in {location} starting at ₹{price_start:,}"
    primary_text = f"Discover premium living at {name}. Prime location, world-class amenities, and prices starting at just ₹{price_start:,}. Book your site visit today."

    return {
        "headline": headline,
        "primary_text": primary_text
    }


def generate_creative_instructions(project):
    return {
        "style": "Clean, luxury real-estate theme",
        "elements": [
            "Project exterior image",
            "Amenities highlight",
            "Starting price banner"
        ]
    }
