CREATE_MATCH_EXAMPLES = {
    "basic": {
        "summary": "Basic upcoming match",
        "description": "Minimal required fields for creating a new match",
        "value": {
            "home_team_id": "1",
            "away_team_id": "2",
            "sport": "football",
            "date": "2026-03-15",
            "status": "upcoming",
            "venue": "Emirates Stadium",
        },
    },
    "completed": {
        "summary": "Completed match",
        "description": "A finished match with a winner",
        "value": {
            "home_team_id": "1",
            "away_team_id": "2",
            "sport": "football",
            "date": "2025-10-26",
            "status": "completed",
            "venue": "Santiago Bernabeu",
            "winner_id": "1",
        },
    },
}


PATCH_MATCH_EXAMPLES = {
    "update_venue": {
        "summary": "Update venue only",
        "description": "Change the match venue without affecting other fields",
        "value": {"venue": "Wembley Stadium"},
    },
    "record_result": {
        "summary": "Record match result",
        "description": "Update a match with completion status and winner",
        "value": {
            "status": "completed",
            "winner_id": "2",
        },
    },
    "reschedule_match": {
        "summary": "Reschedule match date",
        "description": "Change the date and venue for an upcoming match",
        "value": {
            "date": "2026-06-15",
            "venue": "Etihad Stadium",
        },
    },
}

PUT_MATCH_EXAMPLES = {
    "replace_upcoming": {
        "summary": "Replace with upcoming match",
        "description": "Completely replace match data with new upcoming match details",
        "value": {
            "home_team_id": "1",
            "away_team_id": "2",
            "sport": "football",
            "date": "2026-05-20",
            "status": "upcoming",
            "venue": "Etihad Stadium",
        },
    },
    "replace_completed": {
        "summary": "Replace with completed match",
        "description": "Replace entire match with completed match data including winner",
        "value": {
            "home_team_id": "1",
            "away_team_id": "2",
            "sport": "football",
            "date": "2026-05-15",
            "status": "completed",
            "venue": "Wembley Stadium",
            "winner_id": "2",
        },
    },
}
