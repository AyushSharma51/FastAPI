CREATE_MATCH_EXAMPLES = {
    "basic": {
        "summary": "Basic upcoming match",
        "description": "Minimal required fields for creating a new match",
        "value": {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
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
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "sport": "football",
            "date": "2025-10-26",
            "status": "completed",
            "venue": "Santiago Bernabeu",
            "winner": "home_team",
        },
    },
    "with_lineup": {
        "summary": "Match with player lineup",
        "description": "Include starting lineups for both teams",
        "value": {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "sport": "football",
            "date": "2026-03-15",
            "status": "upcoming",
            "venue": "Emirates Stadium",
            "home_lineup": [
                {
                    "number": 1,
                    "name": "Aaron Ramsdale",
                    "position": "goalkeeper",
                    "is_captain": False,
                },
                {
                    "number": 10,
                    "name": "Martin Odegaard",
                    "position": "midfielder",
                    "is_captain": True,
                },
            ],
            "away_lineup": [
                {
                    "number": 1,
                    "name": "Kepa Arrizabalaga",
                    "position": "goalkeeper",
                    "is_captain": False,
                }
            ],
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
            "winner": "home_team",
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
    "add_lineup": {
        "summary": "Add team lineup",
        "description": "Add starting lineup before match",
        "value": {
            "home_lineup": [
                {
                    "number": 1,
                    "name": "Aaron Ramsdale",
                    "position": "goalkeeper",
                    "is_captain": False,
                },
                {
                    "number": 10,
                    "name": "Martin Odegaard",
                    "position": "midfielder",
                    "is_captain": True,
                },
            ]
        },
    },
}

PUT_MATCH_EXAMPLES = {
    "replace_upcoming": {
        "summary": "Replace with upcoming match",
        "description": "Completely replace match data with new upcoming match details",
        "value": {
            "home_team": "Manchester City",
            "away_team": "Tottenham",
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
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "sport": "football",
            "date": "2026-05-15",
            "status": "completed",
            "venue": "Wembley Stadium",
            "winner": "home_team",
        },
    },
}
