#!/usr/bin/env python3
"""
WISDOM ENGINE
Feeds ancient truth into app generation decisions.
Every app the organism builds starts with these questions.
"""

# ═══════════════════════════════════════
# CORE WISDOM PRINCIPLES
# These shape HOW we build, not just WHAT
# ═══════════════════════════════════════

CORE_PRINCIPLES = {
    "tao_water": {
        "teaching": "Be like water — go where others won't, nourish without striving",
        "design_question": "What does this person actually need that no other app gives them?",
        "app_decision": "Lead with the thing nobody else leads with"
    },
    "tao_emptiness": {
        "teaching": "It is the empty space that makes the vessel useful",
        "design_question": "What should we NOT put in this app?",
        "app_decision": "Remove every feature that doesn't serve the real need"
    },
    "stoic_control": {
        "teaching": "Focus only on what you can control",
        "design_question": "What can this person actually change with this app?",
        "app_decision": "Only show information the user can act on"
    },
    "buddhist_suffering": {
        "teaching": "Begin with suffering — what causes pain?",
        "design_question": "What is the worst moment of this person's day?",
        "app_decision": "The first screen relieves that exact pain"
    },
    "confucius_heart": {
        "teaching": "Wherever you go, go with all your heart",
        "design_question": "Does every detail show care for this person?",
        "app_decision": "Tone, color, words — all chosen for them specifically"
    },
    "marcus_action": {
        "teaching": "Waste no time arguing. Do what is right.",
        "design_question": "What is the one action this app must make effortless?",
        "app_decision": "That action takes 3 seconds or less"
    },
    "zen_ordinary": {
        "teaching": "Before and after enlightenment — chop wood, carry water",
        "design_question": "What does this person do every single day?",
        "app_decision": "Make the daily routine beautiful and fast"
    },
    "hermetic_pattern": {
        "teaching": "As above, so below — patterns repeat at every scale",
        "design_question": "What pattern from this domain appears in others?",
        "app_decision": "Cross-pollinate what works across domains"
    }
}

# ═══════════════════════════════════════
# DOMAIN WISDOM PROFILES
# What each domain most needs to hear
# ═══════════════════════════════════════

DOMAIN_WISDOM_PROFILES = {
    "healthcare": {
        "core_truth": "Healing begins before the appointment",
        "wisdom": "Buddhist: Compassion is the wish to relieve suffering — not manage it",
        "design_principle": "Every screen asks: does this reduce anxiety or add to it?",
        "what_to_skip": "Anything that makes the patient feel like a number",
        "lead_with": "Relief — 'Your appointment is confirmed. You are taken care of.'",
        "daily_ritual": "Morning patient list with human names, not IDs",
        "cross_pollinate": ["mental_health", "pharmacy", "telehealth"]
    },
    "law": {
        "core_truth": "Justice is served one case at a time, with full attention",
        "wisdom": "Marcus Aurelius: If it is not right, do not do it. If it is not true, do not say it.",
        "design_principle": "Every screen asks: does this serve the client or the attorney's ego?",
        "what_to_skip": "Complexity that obscures rather than clarifies",
        "lead_with": "What needs attention today — not what was done yesterday",
        "daily_ritual": "Morning case review — urgent first, always",
        "cross_pollinate": ["nonprofit", "mental_health", "insurance"]
    },
    "restaurant": {
        "core_truth": "Every meal is an act of hospitality — feeding body and soul",
        "wisdom": "Zen: Before enlightenment, chop wood. After — chop wood. Excellence is in the ordinary.",
        "design_principle": "Every screen asks: does this help us serve guests better?",
        "what_to_skip": "Analytics that distract from the food and the people",
        "lead_with": "Tonight's reservations and what needs prep right now",
        "daily_ritual": "Pre-service checklist — team ready, food ready, heart ready",
        "cross_pollinate": ["bakery", "catering", "events"]
    },
    "salon": {
        "core_truth": "You are not cutting hair — you are restoring confidence",
        "wisdom": "Tao: The practice itself is the art. Beauty goes deeper than appearance.",
        "design_principle": "Every screen asks: does this let me be fully present with my client?",
        "what_to_skip": "Anything that pulls focus away from the person in the chair",
        "lead_with": "Who is coming today and what they love",
        "daily_ritual": "Morning schedule with client notes — remember their lives",
        "cross_pollinate": ["spa", "beauty", "mental_wellness"]
    },
    "agriculture": {
        "core_truth": "The farmer serves the land — the land serves the farmer",
        "wisdom": "Tao verse 8: Water nourishes all without striving. Work with nature, not against it.",
        "design_principle": "Every screen asks: does this help me read what the land is telling me?",
        "what_to_skip": "Technology that disconnects from the soil and the season",
        "lead_with": "Today's weather, soil conditions, and what needs doing",
        "daily_ritual": "Dawn field report — what does the land need today?",
        "cross_pollinate": ["smart_farm", "nutrition_center", "supply_chain"]
    },
    "smart_farm": {
        "core_truth": "Technology should amplify the farmer's instinct, not replace it",
        "wisdom": "The best fertilizer is the farmer's shadow — presence matters.",
        "design_principle": "Every screen asks: does this make a good farmer better?",
        "what_to_skip": "Data that overwhelms rather than informs",
        "lead_with": "Alerts that matter — what needs attention right now",
        "daily_ritual": "Morning sensor check — what did the farm tell us overnight?",
        "cross_pollinate": ["agriculture", "drone_delivery", "supply_chain"]
    },
    "gym": {
        "core_truth": "You are building people, not bodies",
        "wisdom": "Tao 33: Mastering others is strength. Mastering yourself is true power.",
        "design_principle": "Every screen asks: does this motivate or shame?",
        "what_to_skip": "Metrics that make people feel inadequate",
        "lead_with": "Who hasn't been in lately — reach out before they quit",
        "daily_ritual": "Morning member check — who needs encouragement today?",
        "cross_pollinate": ["mental_wellness", "yoga", "fitness"]
    },
    "pharmacy": {
        "core_truth": "Every prescription is an act of care, not just chemistry",
        "wisdom": "Hippocrates: First, do no harm. Then heal.",
        "design_principle": "Every screen asks: is this patient safe and understood?",
        "what_to_skip": "Speed over accuracy — never",
        "lead_with": "Ready prescriptions and any alerts — patient safety first",
        "daily_ritual": "Morning queue — who is waiting, who needs counseling",
        "cross_pollinate": ["healthcare", "mental_health", "telehealth"]
    },
    "mental-health": {
        "core_truth": "The therapeutic relationship is the medicine",
        "wisdom": "Buddhist Dhammapada: The mind is everything. What we think, we become.",
        "design_principle": "Every screen asks: does this protect the space of healing?",
        "what_to_skip": "Anything clinical that makes the client feel like a diagnosis",
        "lead_with": "Today's sessions with full human context",
        "daily_ritual": "Morning intention — who needs extra care today?",
        "cross_pollinate": ["mental_wellness", "healthcare", "yoga"]
    },
    "nonprofit": {
        "core_truth": "Service is the highest calling — serve from strength, not guilt",
        "wisdom": "Tao verse 8: True goodness nourishes all without seeking recognition.",
        "design_principle": "Every screen asks: does this serve the mission or the organization?",
        "what_to_skip": "Bureaucracy that slows down helping people",
        "lead_with": "Who we helped today and who needs help tomorrow",
        "daily_ritual": "Impact check — real people, real outcomes",
        "cross_pollinate": ["church", "education", "mental_health"]
    },
    "daycare": {
        "core_truth": "You are shaping who they will become",
        "wisdom": "Give a child roots and wings — safety and freedom both.",
        "design_principle": "Every screen asks: would this child's parent feel at peace seeing this?",
        "what_to_skip": "Anything that treats children as inventory",
        "lead_with": "Today's children — who they are, what they need",
        "daily_ritual": "Morning check-in — every child accounted for and welcomed",
        "cross_pollinate": ["school", "education", "mental_wellness"]
    },
    "accounting": {
        "core_truth": "True wealth is freedom — money is just the measure",
        "wisdom": "Tao 44: Know when enough is enough and you will always have enough.",
        "design_principle": "Every screen asks: does this give clarity or create anxiety?",
        "what_to_skip": "Complexity that obscures the simple truth of cash flow",
        "lead_with": "What came in, what went out, what's left — simply",
        "daily_ritual": "Morning numbers — one clear picture of financial health",
        "cross_pollinate": ["freelancer", "realestate", "insurance"]
    },
    "church": {
        "core_truth": "Community is the ministry — people before programs",
        "wisdom": "The greatest leader empties himself of ego and fills his people with confidence.",
        "design_principle": "Every screen asks: does this strengthen our community?",
        "what_to_skip": "Administrative complexity that distracts from pastoral care",
        "lead_with": "Who needs care this week — not schedules",
        "daily_ritual": "Morning prayer list — real names, real needs",
        "cross_pollinate": ["nonprofit", "education", "mental_wellness"]
    },
    "school": {
        "core_truth": "Every child learns differently — meet them where they are",
        "wisdom": "Confucius: Tell me and I forget. Teach me and I remember. Involve me and I learn.",
        "design_principle": "Every screen asks: does this serve the student or the system?",
        "what_to_skip": "Standardization that ignores individual needs",
        "lead_with": "Students who need attention today — not averages",
        "daily_ritual": "Morning attendance with notes — who seems off today?",
        "cross_pollinate": ["daycare", "tutoring", "mental_health"]
    },
    "construction": {
        "core_truth": "What you build outlasts you — build it right",
        "wisdom": "Tao 11: It is the empty space that makes the vessel useful — plan the gaps.",
        "design_principle": "Every screen asks: does this keep the job moving safely?",
        "what_to_skip": "Reports nobody reads — focus on the work",
        "lead_with": "Today's site status and what's blocking progress",
        "daily_ritual": "Morning crew check — safety first, then schedule",
        "cross_pollinate": ["plumber", "autorepair", "fleet_management"]
    },
    "realestate": {
        "core_truth": "Home is where life happens — help people find where they belong",
        "wisdom": "Tao: Water flows to low places others reject and finds its power there.",
        "design_principle": "Every screen asks: does this help match people to places?",
        "what_to_skip": "Data that loses the human story of why they're moving",
        "lead_with": "Active clients and their search — their dream, not just specs",
        "daily_ritual": "Morning pipeline — who is closest to finding home?",
        "cross_pollinate": ["law", "construction", "rental"]
    },
}

DEFAULT_WISDOM_PROFILE = {
    "core_truth": "Serve people first — everything else follows",
    "wisdom": "Tao verse 64: A journey of a thousand miles begins with a single step.",
    "design_principle": "Every screen asks: does this make someone's day easier?",
    "what_to_skip": "Features that impress developers but confuse users",
    "lead_with": "The one thing this person needs most right now",
    "daily_ritual": "Morning check — what matters today?",
    "cross_pollinate": []
}

def get_wisdom_profile(domain_id):
    return DOMAIN_WISDOM_PROFILES.get(domain_id, DEFAULT_WISDOM_PROFILE)

def wisdom_brief(domain_id):
    """Short wisdom injection for generation decisions"""
    p = get_wisdom_profile(domain_id)
    return f"""
WISDOM BRIEF — {domain_id.upper()}
Core truth:      {p['core_truth']}
Ancient wisdom:  {p['wisdom']}
Design law:      {p['design_principle']}
Skip:            {p['what_to_skip']}
Lead with:       {p['lead_with']}
Daily ritual:    {p['daily_ritual']}
Cross-pollinate: {', '.join(p['cross_pollinate']) if p['cross_pollinate'] else 'none yet'}
"""

if __name__ == "__main__":
    for domain in ["law", "salon", "agriculture", "daycare"]:
        print(wisdom_brief(domain))
        print("="*60)
