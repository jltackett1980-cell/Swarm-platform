#!/usr/bin/env python3
import json
from pathlib import Path

freedom_domain = {
    "domain": "freedom_creation",
    "name": "Liberate",
    "tagline": "From survival to creation",
    "color": "#FFD700",
    "user": "any person burdened by survival fear",
    "worst_moment": "too tired, too scared, too busy to create",
    "today_focus": "What can I create today, even for 5 minutes?",
    "human_greeting": "You were born to create. Let's clear the way.",
    "features": [
        "creation_prompt_generator",
        "fear_identifier_tool",
        "survival_needs_checklist",
        "resource_finder",
        "creative_time_blocker",
        "community_creator_connect",
        "offline_first",
        "no_survival_mode_reminder"
    ],
    "wisdom": "The goal is to take survival out of the equation so you can just be creative",
    "constitution_reference": "Article 5 & 3 — interpreted for freedom"
}

out = Path('federation/freedom_creation')
out.mkdir(parents=True, exist_ok=True)
(out / 'node_champion.json').write_text(json.dumps(freedom_domain, indent=2))
print("✅ Created freedom_creation domain — survival → creation")
