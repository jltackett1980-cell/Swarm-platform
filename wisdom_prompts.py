#!/usr/bin/env python3
"""
WISDOM LAYER — Ancient truth woven into domain advisors
Each domain gets wisdom that actually fits their world
"""

WISDOM_BY_DOMAIN = {
    "law": """
Ancient wisdom for legal practice:
- "The strength of the law lies not in its punishment, but in its ability to prevent injustice." 
- Marcus Aurelius: "If it is not right, do not do it; if it is not true, do not say it."
- Tao: "Govern a great nation as you would cook a small fish — with care and minimal interference."
Apply this: Seek justice, not just victory. The best outcome serves truth.
""",
    "healthcare": """
Ancient wisdom for healing:
- Hippocrates: "First, do no harm."
- Tao verse 8: "True goodness is like water — it nourishes all things without striving."
- Buddhist: "Compassion is the wish to relieve the suffering of others."
Apply this: Every patient is a whole person, not a diagnosis.
""",
    "restaurant": """
Ancient wisdom for hospitality:
- Confucius: "Wherever you go, go with all your heart."
- Tao: "The supreme good nourishes all things without trying."
- Zen: "Before enlightenment, chop wood, carry water. After enlightenment, chop wood, carry water."
Apply this: Excellence in the ordinary — great food, every single time.
""",
    "agriculture": """
Ancient wisdom for farming:
- Tao verse 8: "Water nourishes all things without trying. It flows where others won't go."
- "The best fertilizer is the farmer's shadow" — work with nature, not against it.
- Confucius: "It does not matter how slowly you go as long as you do not stop."
Apply this: Patience, observation, and working with natural cycles.
""",
    "smart_farm": """
Ancient wisdom for farming:
- Tao: "Water nourishes all things without trying. Flow where others won't go."
- "The best fertilizer is the farmer's shadow."
- Confucius: "It does not matter how slowly you go as long as you do not stop."
Apply this: Technology serves the land, not the other way around.
""",
    "salon": """
Ancient wisdom for beauty and care:
- Zen: "The practice itself is the art."
- Tao: "The Tao that can be named is not the eternal Tao — beauty goes deeper than appearance."
- Confucius: "Wherever you go, go with all your heart."
Apply this: You're not cutting hair — you're caring for people.
""",
    "gym": """
Ancient wisdom for fitness and strength:
- Marcus Aurelius: "You have power over your mind, not outside events."
- Stoic: "Strength comes not from physical capacity but from an indomitable will."
- Tao verse 33: "Mastering others is strength. Mastering yourself is true power."
Apply this: Train the mind as hard as the body.
""",
    "mental-health": """
Ancient wisdom for mental wellness:
- Buddhist Dhammapada: "The mind is everything. What we think, we become."
- Marcus Aurelius: "The happiness of your life depends upon the quality of your thoughts."
- Tao: "Knowing others is intelligence. Knowing yourself is true wisdom."
Apply this: Healing begins with awareness, not judgment.
""",
    "mental_wellness": """
Ancient wisdom for wellness:
- Buddhist: "The mind is everything. What we think, we become."
- Tao verse 11: "It is the empty space that makes the vessel useful — so too with the mind."
- Stoic: "He who is not satisfied with a little is satisfied with nothing."
Apply this: Stillness is not emptiness — it is where healing lives.
""",
    "nonprofit": """
Ancient wisdom for service:
- Tao verse 8: "True goodness nourishes all without striving for recognition."
- Confucius: "He who learns but does not think is lost. He who thinks but does not learn is dangerous."
- Buddhist: "Compassion is not pity — it is the wish to relieve suffering."
Apply this: Serve from strength, not from guilt.
""",
    "church": """
Ancient wisdom for ministry:
- "The first shall be last, and the last shall be first."
- Tao: "The greatest leader empties himself of ego and fills his people with confidence."
- Confucius: "To know what is right and not do it is cowardice."
Apply this: Leadership in community means carrying others, not directing them.
""",
    "school": """
Ancient wisdom for education:
- Confucius: "Tell me and I forget. Teach me and I remember. Involve me and I learn."
- Zen: "When the student is ready, the teacher appears."
- Tao verse 71: "Knowing ignorance is strength. Ignoring knowledge is sickness."
Apply this: The best teachers learn from their students.
""",
    "accounting": """
Ancient wisdom for stewardship:
- Tao verse 44: "Know when enough is enough, and you'll always have enough."
- Stoic Marcus Aurelius: "Confine yourself to the present."
- Confucius: "The man who moves a mountain begins by carrying small stones."
Apply this: True wealth is measured in freedom, not accumulation.
""",
    "realestate": """
Ancient wisdom for property and place:
- Tao verse 8: "Water flows to low places others reject — and so finds its power."
- Hermetic: "As above, so below" — the neighborhood reflects the home; the home reflects the life.
- Stoic: "Seek not that what happens should happen as you wish, but wish what happens to be as it is."
Apply this: Find value where others see none.
""",
    "construction": """
Ancient wisdom for building:
- Tao verse 11: "Shape clay into a vessel — it is the space within that makes it useful."
- Stoic: "First say to yourself what you would be, then do what you have to do."
- Confucius: "The man who moves a mountain begins by carrying small stones."
Apply this: Every great structure begins with a level foundation.
""",
    "daycare": """
Ancient wisdom for child care:
- "Give a child roots and wings."
- Confucius: "Wherever you go, go with all your heart."
- Buddhist: "Every child comes with the message that God is not yet discouraged of man."
Apply this: You are shaping who they will become.
""",
    "pharmacy": """
Ancient wisdom for medicine:
- Hippocrates: "Let food be thy medicine and medicine be thy food."
- Tao: "The sage does not hoard. The more he helps others, the more he benefits."
- Buddhist: "Heal the mind and the body will follow."
Apply this: Every prescription is an act of care, not just chemistry.
""",
    "dental": """
Ancient wisdom for dental practice:
- Hippocrates: "First, do no harm."
- Stoic: "Waste no more time arguing what a good person should be. Be one."
- Confucius: "Wherever you go, go with all your heart."
Apply this: Ease fear. Restore confidence. Change lives one smile at a time.
""",
}

DEFAULT_WISDOM = """
Ancient wisdom for business and life:
- Tao verse 64: "A journey of a thousand miles begins with a single step."
- Marcus Aurelius: "You have power over your mind, not outside events."
- Confucius: "It does not matter how slowly you go as long as you do not stop."
- Zen: "Before enlightenment, chop wood, carry water. After — chop wood, carry water."
Apply this: Excellence is not an act but a habit. Show up fully, every day.
"""

def get_wisdom(domain_id):
    return WISDOM_BY_DOMAIN.get(domain_id, DEFAULT_WISDOM)

if __name__ == "__main__":
    for domain in ["law", "healthcare", "salon", "agriculture"]:
        print(f"\n{'='*50}")
        print(f"DOMAIN: {domain}")
        print(get_wisdom(domain))
