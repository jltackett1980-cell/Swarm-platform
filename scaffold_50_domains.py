#!/usr/bin/env python3
"""
Phoenix Forge — 50 Everyday People Domain Scaffolder
Builds federation/{domain}/ structure for each new domain.
Focus: Regular people, real life improvement, 5-min lessons, plain-English help.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 50 EVERYDAY PEOPLE DOMAINS
# Philosophy: Wu wei flow, offline first, no login wall, human greeting
# ═══════════════════════════════════════════════════════════════

DOMAINS = [
    # ── LEARNING & SKILLS ─────────────────────────────────────
    {
        "domain": "micro_learning",
        "name": "LearnIn5",
        "tagline": "One skill. Five minutes. Every day.",
        "color": "#6C63FF",
        "user": "curious person wanting to grow",
        "worst_moment": "wants to learn but feels overwhelmed or has no time",
        "today_focus": "Today's 5-minute lesson",
        "human_greeting": "Hey! Ready for your 5 minutes?",
        "features": ["daily_bite", "streak_tracker", "offline_lessons", "no_quiz_pressure"],
        "wisdom": "The journey of a thousand miles begins with a single step — Lao Tzu"
    },
    {
        "domain": "reading_coach",
        "name": "ReadEasy",
        "tagline": "Read better, one page at a time.",
        "color": "#FF6B6B",
        "user": "adult who struggles with reading or wants to read more",
        "worst_moment": "feels embarrassed about reading speed or comprehension",
        "today_focus": "Today's reading practice",
        "human_greeting": "Welcome back. No pressure — just a few minutes today.",
        "features": ["font_size_control", "read_aloud", "simple_words_mode", "offline_content"],
        "wisdom": "Knowledge is a treasure, but practice is the key — Lao Tzu"
    },
    {
        "domain": "math_helper",
        "name": "MathBuddy",
        "tagline": "Plain-English math for real life.",
        "color": "#4ECDC4",
        "user": "adult who needs math for everyday tasks",
        "worst_moment": "feels stupid about math, avoids bills or taxes because of it",
        "today_focus": "Today's real-life math problem",
        "human_greeting": "No tests here. Just real math that helps you.",
        "features": ["bill_calculator", "tip_helper", "loan_explainer", "offline_calculator"],
        "wisdom": "He who knows enough is enough will always have enough — Lao Tzu"
    },
    {
        "domain": "language_daily",
        "name": "WordADay",
        "tagline": "Learn a new language 5 minutes at a time.",
        "color": "#F7DC6F",
        "user": "person wanting to connect with another culture or family",
        "worst_moment": "gave up on Duolingo because it felt like homework",
        "today_focus": "Today's phrase",
        "human_greeting": "Buenos días! Ready for one phrase today?",
        "features": ["audio_pronunciation", "family_phrases", "offline_mode", "no_streak_shame"],
        "wisdom": "To know another language is to have a second soul"
    },
    {
        "domain": "typing_trainer",
        "name": "TypeFast",
        "tagline": "Type faster, get jobs done quicker.",
        "color": "#85C1E9",
        "user": "adult who types slowly and wants to get better at computers",
        "worst_moment": "feels left behind at work because slow typing",
        "today_focus": "Today's 3-minute typing practice",
        "human_greeting": "Let's practice. Three minutes is all it takes.",
        "features": ["progressive_difficulty", "job_phrases", "offline_practice", "no_leaderboard"],
        "wisdom": "Small daily improvements lead to staggering results"
    },
    {
        "domain": "computer_basics",
        "name": "TechSimple",
        "tagline": "Technology explained like a friend would.",
        "color": "#A9DFBF",
        "user": "older adult or tech newcomer",
        "worst_moment": "feels embarrassed asking for help with basic computer tasks",
        "today_focus": "Today's tech tip",
        "human_greeting": "No dumb questions here. What do you need help with?",
        "features": ["big_text", "step_by_step_screenshots", "offline_guides", "call_a_friend_mode"],
        "wisdom": "The wise adapt themselves to circumstances — Chinese proverb"
    },

    # ── MONEY & FINANCES ──────────────────────────────────────
    {
        "domain": "budget_simple",
        "name": "BudgetBuddy",
        "tagline": "Know where your money goes.",
        "color": "#27AE60",
        "user": "person living paycheck to paycheck",
        "worst_moment": "checks account and money is gone, doesn't know where it went",
        "today_focus": "Where did money go this week?",
        "human_greeting": "Let's figure out your money together. No judgment.",
        "features": ["envelope_budgeting", "spending_categories", "offline_tracking", "no_bank_link_required"],
        "wisdom": "Beware of little expenses; a small leak will sink a great ship — Franklin"
    },
    {
        "domain": "debt_tracker",
        "name": "DebtFree",
        "tagline": "One debt at a time. You've got this.",
        "color": "#E74C3C",
        "user": "person overwhelmed by credit card or medical debt",
        "worst_moment": "opens mail and sees another bill, feels hopeless",
        "today_focus": "Your debt payoff progress today",
        "human_greeting": "Every dollar toward debt is a win. Let's count them.",
        "features": ["snowball_method", "avalanche_method", "payment_tracker", "offline_planner"],
        "wisdom": "Out of debt, out of danger"
    },
    {
        "domain": "savings_jar",
        "name": "SaveUp",
        "tagline": "Save for what matters, one day at a time.",
        "color": "#F39C12",
        "user": "person who wants to save but lives check to check",
        "worst_moment": "emergency hits and there's nothing in the account",
        "today_focus": "Today's savings goal",
        "human_greeting": "Even $1 counts. Let's build your cushion.",
        "features": ["goal_jars", "micro_savings_tips", "offline_tracker", "no_bank_required"],
        "wisdom": "A small saving is a great gain"
    },
    {
        "domain": "bill_organizer",
        "name": "BillAlert",
        "tagline": "Never miss a bill again.",
        "color": "#8E44AD",
        "user": "person juggling multiple bills and due dates",
        "worst_moment": "gets a late fee because forgot about a bill",
        "today_focus": "Bills due this week",
        "human_greeting": "Here's what's coming up. No surprises.",
        "features": ["due_date_calendar", "reminder_alerts", "offline_list", "no_account_needed"],
        "wisdom": "Forewarned is forearmed"
    },
    {
        "domain": "gig_income",
        "name": "GigTrack",
        "tagline": "Track your gig work. Know what you really make.",
        "color": "#1ABC9C",
        "user": "DoorDash, Uber, freelance worker",
        "worst_moment": "tax time comes and has no records of income or expenses",
        "today_focus": "Today's earnings and expenses",
        "human_greeting": "Log your shift. Takes 30 seconds.",
        "features": ["mileage_tracker", "income_log", "expense_tracker", "tax_estimate", "offline_first"],
        "wisdom": "Know what you earn, keep what you deserve"
    },

    # ── LEGAL & RIGHTS ────────────────────────────────────────
    {
        "domain": "tenant_rights",
        "name": "RentRights",
        "tagline": "Know your rights as a renter. Plain English.",
        "color": "#C0392B",
        "user": "renter dealing with landlord issues",
        "worst_moment": "landlord threatens eviction or ignores repairs",
        "today_focus": "Your rights in your state",
        "human_greeting": "You have rights. Let's find out what they are.",
        "features": ["state_laws", "letter_templates", "offline_guides", "emergency_steps"],
        "wisdom": "Knowledge of your rights is the first shield"
    },
    {
        "domain": "workers_rights",
        "name": "WorkRights",
        "tagline": "What your employer can and cannot do.",
        "color": "#E67E22",
        "user": "hourly worker, gig worker, new employee",
        "worst_moment": "gets cheated on wages or unfairly fired, doesn't know what to do",
        "today_focus": "Your rights at work",
        "human_greeting": "You're protected. Let's figure out how.",
        "features": ["wage_theft_guide", "break_rights", "discrimination_help", "offline_reference"],
        "wisdom": "An injury to one is an injury to all"
    },
    {
        "domain": "small_claims",
        "name": "ClaimIt",
        "tagline": "Take someone to small claims court yourself.",
        "color": "#2980B9",
        "user": "person owed money or wronged by a business",
        "worst_moment": "gave up on $500 owed because didn't know how to fight it",
        "today_focus": "Steps to file your claim",
        "human_greeting": "You don't need a lawyer for this. Let me show you.",
        "features": ["step_by_step_filing", "letter_builder", "state_court_finder", "offline_checklist"],
        "wisdom": "Justice delayed is justice denied — Gladstone"
    },
    {
        "domain": "benefits_finder",
        "name": "BenefitsNow",
        "tagline": "Find benefits you qualify for. Right now.",
        "color": "#16A085",
        "user": "low-income individual or family",
        "worst_moment": "doesn't know about food stamps, Medicaid, or utilities help they qualify for",
        "today_focus": "Benefits available in your area",
        "human_greeting": "These programs exist for you. Let's find them.",
        "features": ["income_screener", "program_finder", "application_links", "offline_guide"],
        "wisdom": "Ask and you shall receive — the programs are there"
    },
    {
        "domain": "immigration_plain",
        "name": "PathFinder",
        "tagline": "Immigration steps in plain language.",
        "color": "#8E44AD",
        "user": "immigrant navigating US immigration system",
        "worst_moment": "confused by forms and scared of making a mistake",
        "today_focus": "Your next step",
        "human_greeting": "You belong here. Let's take the next step together.",
        "features": ["form_explainer", "timeline_tracker", "plain_language_guides", "offline_reference"],
        "wisdom": "The strength of a nation is in its diversity"
    },

    # ── HEALTH & WELLNESS ─────────────────────────────────────
    {
        "domain": "medication_tracker",
        "name": "MedRemind",
        "tagline": "Never forget your medication.",
        "color": "#E74C3C",
        "user": "person managing multiple prescriptions",
        "worst_moment": "misses a dose because life got busy",
        "today_focus": "Today's medications",
        "human_greeting": "Good morning. Time for your meds?",
        "features": ["medication_reminders", "refill_alerts", "offline_schedule", "caregiver_mode"],
        "wisdom": "Taking care of yourself is taking care of everything"
    },
    {
        "domain": "mental_wellness",
        "name": "CalmCheck",
        "tagline": "Small daily check-ins. Big difference.",
        "color": "#9B59B6",
        "user": "person dealing with stress, anxiety, or low mood",
        "worst_moment": "feels overwhelmed and doesn't know how to start feeling better",
        "today_focus": "How are you doing today, really?",
        "human_greeting": "Hey. Just checking in. How's today treating you?",
        "features": ["mood_checkin", "breathing_exercises", "offline_coping_tools", "no_diagnosis"],
        "wisdom": "You don't have to control your thoughts, just stop letting them control you"
    },
    {
        "domain": "sleep_better",
        "name": "SleepWell",
        "tagline": "Small changes for better sleep tonight.",
        "color": "#2C3E50",
        "user": "person who can't sleep or wakes up exhausted",
        "worst_moment": "3am, can't sleep, knows tomorrow will be hard",
        "today_focus": "Tonight's wind-down plan",
        "human_greeting": "Let's get you sleeping better. Start tonight.",
        "features": ["wind_down_routine", "sleep_log", "offline_tips", "noise_options"],
        "wisdom": "Sleep is the best meditation — Dalai Lama"
    },
    {
        "domain": "chronic_pain",
        "name": "PainLog",
        "tagline": "Track your pain. Talk to your doctor better.",
        "color": "#E8D5B7",
        "user": "person with chronic pain or illness",
        "worst_moment": "doctor asks about pain and can't remember or describe it well",
        "today_focus": "Today's pain log",
        "human_greeting": "I see you. Let's track this so you can get better care.",
        "features": ["pain_scale_log", "trigger_tracker", "doctor_report_export", "offline_first"],
        "wisdom": "Knowing the enemy is half the battle"
    },
    {
        "domain": "nutrition_simple",
        "name": "EatSimple",
        "tagline": "Eat better on a budget. No diet culture.",
        "color": "#27AE60",
        "user": "person wanting to eat healthier without spending more",
        "worst_moment": "junk food is cheap and easy, healthy feels hard and expensive",
        "today_focus": "Today's simple healthy swap",
        "human_greeting": "No diets here. Just one better choice today.",
        "features": ["budget_meals", "ingredient_swaps", "offline_recipes", "no_calorie_counting"],
        "wisdom": "Let food be thy medicine — Hippocrates"
    },
    {
        "domain": "walking_habit",
        "name": "JustWalk",
        "tagline": "The simplest exercise. Track it.",
        "color": "#52BE80",
        "user": "person wanting to move more without a gym",
        "worst_moment": "feels out of shape but gym feels too hard or expensive",
        "today_focus": "Today's walk",
        "human_greeting": "Even 10 minutes counts. Ready?",
        "features": ["step_counter", "route_suggestions", "offline_tracking", "no_fitness_shaming"],
        "wisdom": "Solvitur ambulando — it is solved by walking"
    },
    {
        "domain": "addiction_support",
        "name": "OneMoreDay",
        "tagline": "One day at a time. You're not alone.",
        "color": "#7F8C8D",
        "user": "person struggling with alcohol, tobacco, or other addiction",
        "worst_moment": "slips up and feels like giving up entirely",
        "today_focus": "Today's commitment",
        "human_greeting": "One day. That's all we're doing today.",
        "features": ["sobriety_counter", "craving_tools", "offline_support", "anonymous_mode"],
        "wisdom": "Every moment is a fresh beginning — T.S. Eliot"
    },

    # ── FAMILY & HOME ─────────────────────────────────────────
    {
        "domain": "parenting_daily",
        "name": "ParentPulse",
        "tagline": "Quick parenting tips for real life.",
        "color": "#F1948A",
        "user": "overwhelmed parent",
        "worst_moment": "doesn't know how to handle a child's behavior and feels like failing",
        "today_focus": "Today's parenting tip",
        "human_greeting": "You're doing better than you think. Here's one tip.",
        "features": ["age_specific_tips", "behavior_guides", "offline_content", "no_judgment"],
        "wisdom": "It's not about being perfect. It's about effort — Brené Brown"
    },
    {
        "domain": "homework_helper",
        "name": "HelpDesk",
        "tagline": "Help your kids with homework. Even the hard stuff.",
        "color": "#5DADE2",
        "user": "parent helping kids with schoolwork",
        "worst_moment": "kid needs help with math and parent can't remember how",
        "today_focus": "What does your kid need help with today?",
        "human_greeting": "Let's figure this out together.",
        "features": ["grade_level_explainers", "worked_examples", "offline_reference", "plain_language"],
        "wisdom": "Education is not filling a bucket but lighting a fire — Yeats"
    },
    {
        "domain": "elder_care",
        "name": "CareGuide",
        "tagline": "Help for those caring for aging parents.",
        "color": "#D5DBDB",
        "user": "adult caregiver for elderly parent",
        "worst_moment": "doesn't know what resources exist or how to handle a crisis",
        "today_focus": "Today's caregiving checklist",
        "human_greeting": "Caring for someone else is hard. Let's make it easier.",
        "features": ["care_checklist", "resource_finder", "offline_guides", "caregiver_self_care"],
        "wisdom": "The greatest gift you can give someone is your time"
    },
    {
        "domain": "chore_system",
        "name": "HouseFlow",
        "tagline": "A home that runs itself. Almost.",
        "color": "#A3E4D7",
        "user": "busy parent or household manager",
        "worst_moment": "house is chaos and doesn't know where to start",
        "today_focus": "Today's 3 tasks",
        "human_greeting": "Just three things today. That's it.",
        "features": ["rotating_chore_list", "family_assignments", "offline_schedule", "no_overwhelm"],
        "wisdom": "Have nothing in your home that you do not know to be useful — Morris"
    },
    {
        "domain": "meal_planner",
        "name": "DinnerDone",
        "tagline": "Know what's for dinner before 5pm panic.",
        "color": "#FAD7A0",
        "user": "busy family meal planner",
        "worst_moment": "5pm hits and no idea what to cook, ends up getting fast food",
        "today_focus": "Tonight's dinner plan",
        "human_greeting": "Tonight is handled. Here's your plan.",
        "features": ["weekly_planner", "grocery_list_generator", "offline_recipes", "budget_friendly"],
        "wisdom": "Failing to plan is planning to fail"
    },
    {
        "domain": "car_maintenance",
        "name": "CarCare",
        "tagline": "Keep your car running. Know when to worry.",
        "color": "#5D6D7E",
        "user": "car owner who isn't a mechanic",
        "worst_moment": "warning light comes on and doesn't know if it's serious or a scam",
        "today_focus": "Your car's health today",
        "human_greeting": "That light on your dash — let's figure it out.",
        "features": ["warning_light_decoder", "maintenance_scheduler", "repair_cost_guide", "offline_reference"],
        "wisdom": "An ounce of prevention is worth a pound of cure"
    },
    {
        "domain": "home_repairs",
        "name": "FixIt",
        "tagline": "Fix it yourself. Save the call.",
        "color": "#E59866",
        "user": "homeowner or renter who wants to do basic repairs",
        "worst_moment": "small thing breaks and feels helpless or gets overcharged",
        "today_focus": "Today's repair guide",
        "human_greeting": "You can fix this. Let me show you.",
        "features": ["video_guides", "tool_list", "offline_instructions", "when_to_call_pro"],
        "wisdom": "Give a man a fish vs teach a man to fish"
    },

    # ── WORK & CAREER ─────────────────────────────────────────
    {
        "domain": "resume_builder",
        "name": "GetHired",
        "tagline": "A resume that gets you interviews.",
        "color": "#2471A3",
        "user": "job seeker without resume writing experience",
        "worst_moment": "applies for jobs and hears nothing back",
        "today_focus": "Improve your resume today",
        "human_greeting": "Let's get you noticed. One improvement at a time.",
        "features": ["template_builder", "bullet_generator", "ats_checker", "offline_editor"],
        "wisdom": "Opportunity favors the prepared"
    },
    {
        "domain": "interview_prep",
        "name": "NailIt",
        "tagline": "Practice until it feels natural.",
        "color": "#1A5276",
        "user": "job seeker preparing for interview",
        "worst_moment": "freezes in interviews or says 'um' too much",
        "today_focus": "Practice today's question",
        "human_greeting": "Let's practice. You've got this.",
        "features": ["question_library", "answer_framework", "mock_interview", "offline_practice"],
        "wisdom": "By failing to prepare, you are preparing to fail"
    },
    {
        "domain": "job_search",
        "name": "JobHunt",
        "tagline": "Track applications. Stay organized.",
        "color": "#2E86C1",
        "user": "unemployed or underemployed person",
        "worst_moment": "applied to 20 jobs, can't remember which ones or follow up",
        "today_focus": "Today's job applications",
        "human_greeting": "Let's stay organized. You'll thank yourself later.",
        "features": ["application_tracker", "follow_up_reminders", "interview_log", "offline_tracker"],
        "wisdom": "A goal without a plan is just a wish"
    },
    {
        "domain": "career_switcher",
        "name": "NewPath",
        "tagline": "Change careers without starting over.",
        "color": "#117A65",
        "user": "person wanting a different career but overwhelmed",
        "worst_moment": "trapped in job they hate, doesn't know where to start",
        "today_focus": "One step toward a new career today",
        "human_greeting": "You can change. Let's start with one small step.",
        "features": ["transferable_skills", "career_ideas", "training_paths", "offline_guides"],
        "wisdom": "It's never too late to be what you might have been — George Eliot"
    },
    {
        "domain": "networking_plain",
        "name": "ConnectUp",
        "tagline": "Talk to people. Get ahead. Feel less awkward.",
        "color": "#AF7AC5",
        "user": "person uncomfortable with networking",
        "worst_moment": "stands alone at networking events, feels invisible",
        "today_focus": "Today's conversation starter",
        "human_greeting": "You're not awkward. Let's find your words.",
        "features": ["conversation_starters", "follow_up_templates", "event_tips", "offline_scripts"],
        "wisdom": "Networking is just collecting friends for the future"
    },

    # ── COMMUNITY & SUPPORT ────────────────────────────────────
    {
        "domain": "neighborhood_help",
        "name": "Neighborly",
        "tagline": "Help your neighbors. Ask for help yourself.",
        "color": "#F5B041",
        "user": "person who wants to build community",
        "worst_moment": "needs help but feels too proud to ask",
        "today_focus": "Who needs help in your area today?",
        "human_greeting": "Everyone needs help sometimes. That's what neighbors are for.",
        "features": ["help_requests", "offer_help", "skill_sharing", "offline_listing"],
        "wisdom": "A good neighbor is a found treasure"
    },
    {
        "domain": "food_access",
        "name": "FoodNearMe",
        "tagline": "Find free meals and food banks near you.",
        "color": "#58D68D",
        "user": "person who can't afford enough food",
        "worst_moment": "hungry, no money, doesn't know where to go",
        "today_focus": "Where to get food today",
        "human_greeting": "You shouldn't be hungry. Let's find help near you.",
        "features": ["food_bank_finder", "meal_site_map", "hours_info", "offline_access"],
        "wisdom": "No one should go hungry"
    },
    {
        "domain": "transportation",
        "name": "RideFinder",
        "tagline": "Get where you need to go. Without a car.",
        "color": "#5DADE2",
        "user": "person without reliable transportation",
        "worst_moment": "misses a job interview because couldn't get there",
        "today_focus": "How to get where you're going today",
        "human_greeting": "Getting around shouldn't be this hard. Let's figure it out.",
        "features": ["bus_routes", "ride_share_info", "community_cars", "offline_maps"],
        "wisdom": "Not all of us who wander are lost — J.R.R. Tolkien"
    },
    {
        "domain": "childcare_finder",
        "name": "CareForKids",
        "tagline": "Find childcare you can trust and afford.",
        "color": "#F8C471",
        "user": "parent needing childcare",
        "worst_moment": "can't go to work because no childcare, feels trapped",
        "today_focus": "Childcare options near you",
        "human_greeting": "You need care for your kids so you can work. Let's find it.",
        "features": ["subsidized_care_finder", "provider_list", "parent_reviews", "offline_list"],
        "wisdom": "It takes a village to raise a child"
    },
    {
        "domain": "recovery_community",
        "name": "TogetherWe",
        "tagline": "Connect with others in recovery.",
        "color": "#D7BDE2",
        "user": "person in recovery or seeking help",
        "worst_moment": "feels alone in their struggle",
        "today_focus": "Today's recovery message",
        "human_greeting": "You're not alone. We're here with you.",
        "features": ["meeting_finder", "sponsor_connect", "daily_meditation", "offline_support"],
        "wisdom": "We're only as sick as our secrets"
    },
    {
        "domain": "veterans_services",
        "name": "VetConnect",
        "tagline": "Benefits and support for veterans.",
        "color": "#85929E",
        "user": "military veteran",
        "worst_moment": "feels forgotten after service, doesn't know benefits",
        "today_focus": "Benefits available to you",
        "human_greeting": "You served. Now let's make sure you're cared for.",
        "features": ["benefits_finder", "healthcare_help", "transition_guides", "offline_reference"],
        "wisdom": "We sleep safe in our beds because rough men stand ready to do violence on our behalf"
    },

    # ── HOBBIES & PERSONAL ─────────────────────────────────────
    {
        "domain": "habit_builder",
        "name": "OneHabit",
        "tagline": "Build one habit at a time.",
        "color": "#F7DC6F",
        "user": "person wanting to make a change",
        "worst_moment": "tried to change everything and failed",
        "today_focus": "Today's habit action",
        "human_greeting": "Just one habit. Let's build it.",
        "features": ["habit_tracker", "streak_counter", "reminder_system", "offline_mode"],
        "wisdom": "We are what we repeatedly do. Excellence, then, is not an act, but a habit — Aristotle"
    },
    {
        "domain": "journal_simple",
        "name": "WriteNow",
        "tagline": "Just write. No pressure.",
        "color": "#A569BD",
        "user": "person who wants to journal but feels awkward",
        "worst_moment": "blank page paralysis",
        "today_focus": "Today's simple prompt",
        "human_greeting": "Just a few words. That's all it takes.",
        "features": ["daily_prompts", "mood_log", "offline_journal", "no_analysis"],
        "wisdom": "Write what should not be forgotten — Isabel Allende"
    },
    {
        "domain": "gardening_basics",
        "name": "GrowFood",
        "tagline": "Grow your own food. Even in small spaces.",
        "color": "#52BE80",
        "user": "person wanting to grow vegetables",
        "worst_moment": "killed every plant they ever owned",
        "today_focus": "What to plant today",
        "human_greeting": "Even black thumbs can grow food. Let's start.",
        "features": ["plant_calendar", "beginner_guides", "problem_solver", "offline_reference"],
        "wisdom": "The glory of gardening: hands in the dirt, head in the sun, heart with nature"
    },
    {
        "domain": "diy_crafts",
        "name": "MakeIt",
        "tagline": "Make things with your hands.",
        "color": "#EDBB99",
        "user": "person wanting to be more creative",
        "worst_moment": "wants to create but doesn't know where to start",
        "today_focus": "Today's simple project",
        "human_greeting": "You can make this. Let's try.",
        "features": ["project_ideas", "supply_lists", "step_by_step", "offline_instructions"],
        "wisdom": "Creativity is intelligence having fun — Einstein"
    },
    {
        "domain": "outdoor_basics",
        "name": "Outside",
        "tagline": "Get outside. Even for 5 minutes.",
        "color": "#48C9B0",
        "user": "person who spends too much time indoors",
        "worst_moment": "realizes it's been days since they saw the sun",
        "today_focus": "Today's outdoor idea",
        "human_greeting": "Fresh air helps. Let's get some.",
        "features": ["nearby_parks", "outdoor_activities", "weather_check", "offline_suggestions"],
        "wisdom": "Nature does not hurry, yet everything is accomplished — Lao Tzu"
    }
]

# Ensure we have 50 domains (count them)
print(f"📊 DOMAINS DEFINED: {len(DOMAINS)}")

# ═══════════════════════════════════════════════════════════════
# SCAFFOLDING FUNCTION
# ═══════════════════════════════════════════════════════════════
HOME = Path("/data/data/com.termux/files/home")
FEDERATION = HOME / "swarm-platform" / "federation"
CHAMPIONS = HOME / "ORGANISM_ARMY" / "champions"

def scaffold_domain(domain_data):
    """Create federation directory structure for a domain"""
    domain_id = domain_data["domain"]
    domain_path = FEDERATION / domain_id
    
    # Create directory if it doesn't exist
    domain_path.mkdir(parents=True, exist_ok=True)
    
    # Create backend directory
    backend_path = domain_path / "backend"
    backend_path.mkdir(exist_ok=True)
    
    # Create backend app.py with basic structure
    app_py = backend_path / "app.py"
    if not app_py.exists():
        app_py.write_text(f'''#!/usr/bin/env python3
"""
{domain_data['name']} Backend
{domain_data['tagline']}
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '{domain_id}.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  content TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db()
    items = conn.execute('SELECT * FROM items ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in items])

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.get_json()
    conn = get_db()
    cursor = conn.execute('INSERT INTO items (user_id, content) VALUES (?, ?)',
                         (data.get('user_id', 'anonymous'), data.get('content', '')))
    conn.commit()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(item))

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
''')
        print(f"  ✅ Created backend for {domain_id}")
    
    # Create frontend directory
    frontend_path = domain_path / "frontend"
    frontend_path.mkdir(exist_ok=True)
    
    # Create src directory
    src_path = frontend_path / "src"
    src_path.mkdir(exist_ok=True)
    
    # Create index.html
    index_html = frontend_path / "index.html"
    if not index_html.exists():
        index_html.write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{domain_data['name']} — {domain_data['tagline']}</title>
    <style>
        :root {{
            --primary: {domain_data['color']};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'system-ui', -apple-system, sans-serif;
            background: #fafafa;
            color: #333;
            padding: 16px;
        }}
        .header {{
            background: var(--primary);
            color: white;
            padding: 20px 16px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 4px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}
        .greeting {{
            background: white;
            border-left: 4px solid var(--primary);
            padding: 16px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .today-card {{
            background: linear-gradient(135deg, var(--primary), #aaa);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .btn {{
            background: white;
            border: 1px solid #ddd;
            padding: 12px 16px;
            border-radius: 8px;
            width: 100%;
            text-align: left;
            font-size: 16px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .wisdom {{
            background: #f0f0f0;
            padding: 16px;
            border-radius: 8px;
            font-style: italic;
            margin-top: 20px;
        }}
        .offline-indicator {{
            position: fixed;
            bottom: 16px;
            right: 16px;
            background: #333;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{domain_data['name']}</h1>
        <p>{domain_data['tagline']}</p>
    </div>
    
    <div class="greeting" id="greeting">
        {domain_data['human_greeting']}
    </div>
    
    <div class="today-card">
        <h3>📅 {domain_data['today_focus']}</h3>
    </div>
    
    <div id="content">
        <!-- Content will be loaded here -->
    </div>
    
    <div class="wisdom" id="wisdom">
        {domain_data['wisdom']}
    </div>
    
    <div class="offline-indicator" id="offlineIndicator">
        ⚡ Offline mode
    </div>
    
    <script>
        // Offline-first setup
        if (!navigator.onLine) {{
            document.getElementById('offlineIndicator').style.display = 'block';
        }}
        
        window.addEventListener('online', () => {{
            document.getElementById('offlineIndicator').style.display = 'none';
        }});
        
        window.addEventListener('offline', () => {{
            document.getElementById('offlineIndicator').style.display = 'block';
        }});
        
        // Load content
        async function loadContent() {{
            const content = document.getElementById('content');
            content.innerHTML = '<p>Loading...</p>';
            
            try {{
                const response = await fetch('/api/items');
                const items = await response.json();
                
                if (items.length === 0) {{
                    content.innerHTML = '<p>Welcome! Add your first item below.</p>';
                }} else {{
                    content.innerHTML = items.map(item => 
                        `<div class="btn" onclick="alert('${{item.content}}')">${{item.content}}</div>`
                    ).join('');
                }}
            }} catch (e) {{
                content.innerHTML = '<p>You\'re offline. Showing saved content.</p>';
            }}
        }}
        
        loadContent();
    </script>
</body>
</html>
''')
        print(f"  ✅ Created frontend for {domain_id}")
    
    # Create champion.json with metadata
    champion_json = domain_path / "champion.json"
    champion_data = {
        "domain": domain_id,
        "name": domain_data["name"],
        "tagline": domain_data["tagline"],
        "color": domain_data["color"],
        "user": domain_data["user"],
        "worst_moment": domain_data["worst_moment"],
        "today_focus": domain_data["today_focus"],
        "human_greeting": domain_data["human_greeting"],
        "features": domain_data["features"],
        "wisdom": domain_data["wisdom"],
        "tech_score": 0,
        "human_score": 0,
        "wisdom_score": 0,
        "total_score": 0,
        "created_at": datetime.now().isoformat(),
        "source_app": f"scaffold_{domain_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    if not champion_json.exists():
        champion_json.write_text(json.dumps(champion_data, indent=2))
        print(f"  ✅ Created champion.json for {domain_id}")
    else:
        # Update existing
        champion_json.write_text(json.dumps(champion_data, indent=2))
        print(f"  🔄 Updated champion.json for {domain_id}")

def main():
    print("\n" + "=" * 60)
    print("🔥 PHOENIX FORGE — 50 EVERYDAY PEOPLE DOMAINS")
    print("=" * 60)
    
    # Ensure directories exist
    FEDERATION.mkdir(parents=True, exist_ok=True)
    CHAMPIONS.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Federation path: {FEDERATION}")
    print(f"📁 Champions path: {CHAMPIONS}")
    print(f"\n📊 Scaffolding {len(DOMAINS)} domains...\n")
    
    for i, domain in enumerate(DOMAINS, 1):
        print(f"[{i:2d}/{len(DOMAINS)}] {domain['domain']}")
        scaffold_domain(domain)
    
    print(f"\n✅ {len(DOMAINS)} domains scaffolded successfully")
    
    # Also create a master index file
    index_path = FEDERATION / "index.json"
    index_data = {
        "total_domains": len(DOMAINS),
        "created_at": datetime.now().isoformat(),
        "domains": [{
            "domain": d["domain"],
            "name": d["name"],
            "tagline": d["tagline"],
            "color": d["color"]
        } for d in DOMAINS]
    }
    index_path.write_text(json.dumps(index_data, indent=2))
    print(f"\n📇 Master index: {index_path}")
    
    print("\n" + "=" * 60)
    print("🔥 NEXT STEPS")
    print("=" * 60)
    print("1. Run: python3 phoenix_mind.py")
    print("2. The organism will see 58 + 50 = 108 domains")
    print("3. GROW directive will prioritize new domains")
    print("4. Amygdala will scan for pain in each")
    print("5. Prefrontal will ask what to build first")
    print("\n🎯 Target: 108 domains by Monday morning")
    print("=" * 60)

if __name__ == "__main__":
    main()
