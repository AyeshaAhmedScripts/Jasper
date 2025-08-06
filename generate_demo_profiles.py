import json
import random
import uuid
import os

first_names = [
    "Aiden", "Lara", "Marcus", "Jasmine", "Tanya", "Carlos", "Nina", "Eli", "Grace", "Zane",
    "Leila", "Victor", "Dia", "Rosa", "Noah", "Harper", "Ivy", "Mason", "Riley", "Liam"
]

last_names = [
    "Stone", "Khan", "Walker", "Kim", "Vega", "Watson", "Reed", "Lopez", "Frost", "Nguyen",
    "Bishop", "Smith", "Sato", "Grant", "Wells", "Ali", "Drake", "Choi", "Murphy", "James"
]

roles = [
    "Civilian", "Medic", "Fighter", "Scientist", "Engineer", "Scout", "Sniper", "Leader",
    "Cook", "Mechanic", "Farmer", "Hacker", "Driver", "Guard", "Survivalist", "Builder"
]

skills_pool = [
    "First Aid", "Cooking", "Sharpshooting", "Engineering", "Stealth", "Tracking",
    "Hacking", "Survival", "Repair", "Bartering", "Negotiation", "Medical Training",
    "Botany", "Scouting", "Wilderness Survival", "Explosives"
]

statuses = ["Alive", "Injured", "Zombie", "Missing"]
priorities = ["Low", "Medium", "High", "Critical"]
locations = ["Zone A", "Zone B", "Safehouse", "Tower Ruins", "Camp Echo", "Sector 5"]

used_names = set()

def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.split())

def generate_profile():
    while True:
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        if full_name not in used_names:
            used_names.add(full_name)
            break

    role = random.choice(roles)
    skills = random.sample(skills_pool, random.randint(2, 4))
    location = random.choice(locations)
    status = random.choice(statuses)
    priority = random.choice(priorities)
    age = random.randint(16, 70)
    contact = f"+92-3{random.randint(100000000, 999999999)}"
    emergency = f"Channel-{random.randint(1, 10)}"
    description = f"{full_name} is a skilled {role.lower()} known for {random.choice(skills).lower()} and {random.choice(skills).lower()}."

    return {
        "id": str(uuid.uuid4()),
        "name": full_name,
        "role": role,
        "skills": skills,
        "location": location,
        "status": status,
        "priority": priority,
        "age": age,
        "contact": contact,
        "emergency": emergency,
        "description": description
    }

def create_demo_profiles(path='profiles.json', count=110, overwrite=True):
    profiles = []

    if os.path.exists(path) and not overwrite:
        with open(path, 'r') as f:
            try:
                profiles = json.load(f)
                for profile in profiles:
                    used_names.add(profile["name"])
            except json.JSONDecodeError:
                profiles = []

    new_profiles = []
    while len(new_profiles) < count:
        profile = generate_profile()
        new_profiles.append(profile)

    if overwrite:
        profiles = new_profiles
    else:
        profiles.extend(new_profiles)

    with open(path, 'w') as f:
        json.dump(profiles, f, indent=2)

    print(f"{count} unique demo survivor profiles {'created' if overwrite else 'added'} in '{path}'.")

if __name__ == '__main__':
    create_demo_profiles()
