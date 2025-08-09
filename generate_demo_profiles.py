# generate_profile.py
import random
import uuid
from app import db, Survivor  # Import your db and Survivor model from app.py

# --- Data Pools ---
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
health_levels = ["Low", "Medium", "High", "Critical"]
locations = ["Zone A", "Zone B", "Safehouse", "Tower Ruins", "Camp Echo", "Sector 5"]

used_names = set()

# --- Helper Functions ---
def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.strip().split())

def generate_unique_id():
    return str(uuid.uuid4())

def generate_profile():
    while True:
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        if full_name not in used_names:
            used_names.add(full_name)
            break

    role = random.choice(roles)
    skills = ', '.join(random.sample(skills_pool, random.randint(2, 4)))
    location = random.choice(locations)
    status = random.choice(statuses)
    health_status = random.choice(health_levels)
    age = random.randint(16, 70)
    contact = f"+92-3{random.randint(100000000, 999999999)}"
    emergency = f"Channel-{random.randint(1, 10)}"
    description = f"{full_name} is a skilled {role.lower()} known for {random.choice(skills_pool).lower()} and {random.choice(skills_pool).lower()}."

    return Survivor(
        id=generate_unique_id(),
        name=full_name,
        role=role,
        skills=skills,
        location=location,
        status=status,
        health_status=health_status,
        age=age,
        contact=contact,
        emergency=emergency,
        description=description
    )

# --- Main Execution ---
if __name__ == "__main__":
    print("Generating 10 random survivor profiles...")
    for _ in range(10):
        profile = generate_profile()
        db.session.add(profile)
    db.session.commit()
    print("✅ Successfully added 10 demo profiles to the database.")
