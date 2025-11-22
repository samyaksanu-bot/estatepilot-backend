def calculate_score(lead):
    score = 0

    # Budget scoring
    try:
        budget = int(lead.get("budget", 0))
        if budget >= 3000000:
            score += 30
        elif budget >= 1500000:
            score += 20
        else:
            score += 10
    except:
        score += 5

    # Location scoring
    if "location" in lead and lead["location"]:
        score += 20

    # Responsiveness scoring
    if lead.get("messages_count", 0) > 3:
        score += 25

    # Name provided
    if lead.get("name"):
        score += 10

    # Always cap at 100
    return min(score, 100)
