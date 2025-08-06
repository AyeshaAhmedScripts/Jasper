from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import json
import uuid
from urllib.parse import unquote
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Replace with your actual PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Goldenmaknae7@localhost:5432/jasper1'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


app.secret_key = "super-secret-key"

# JSON Files
PROFILE_FILE = "profiles.json"
TAG_FILE = "map_tags.json"



class Survivor(db.Model):
    __tablename__ = 'survivors'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    skills = db.Column(db.Text)  # comma-separated skills
    location = db.Column(db.String(100))
    status = db.Column(db.String(30))
    health_status = db.Column(db.String(30))
    age = db.Column(db.Integer)
    contact = db.Column(db.String(30))
    emergency = db.Column(db.String(50))
    description = db.Column(db.Text)



class MapTag(db.Model):
    __tablename__ = 'map_tags'

    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.String(36), db.ForeignKey('survivors.id'))  # Links to Survivor
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    tag = db.Column(db.String(100))
    status = db.Column(db.String(30))  # e.g. Pending, Verified
    timestamp = db.Column(db.BigInteger)  # Stored as UNIX ms timestamp
    up = db.Column(db.Integer, default=0)
    down = db.Column(db.Integer, default=0)

    survivor = db.relationship('Survivor', backref='tags')


# ------------------ Helper Functions ------------------

# Profile helpers
def load_profiles():
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_profiles(profiles):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.strip().split())

def generate_unique_id():
    return str(uuid.uuid4())

# Tag helpers
def load_tags():
    if os.path.exists(TAG_FILE):
        with open(TAG_FILE, "r") as f:
            return json.load(f)
    return []

def save_tags(tags):
    with open(TAG_FILE, "w") as f:
        json.dump(tags, f, indent=2)

# ------------------ Profile Routes ------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profiles", methods=["GET"])
def get_profiles():
    return jsonify(load_profiles())

@app.route("/all-profiles")
def all_profiles():
    sort_by = request.args.get('sort_by', 'name')
    profiles = load_profiles()
    if sort_by in ['name', 'status', 'role']:
        profiles.sort(key=lambda p: p.get(sort_by, '').lower())
    return render_template("all_profiles.html", profiles=profiles)

@app.route("/profile-details/<id>")
def legacy_profile_details(id):
    profiles = load_profiles()
    for p in profiles:
        if p.get("id") == id:
            return render_template("profile_details.html", profile=p)
    flash("Profile not found.", "error")
    return redirect(url_for('all_profiles'))

@app.route("/add-profile", methods=["GET", "POST"])
def add_profile():
    if request.method == "POST":
        name = capitalize_words(request.form.get("name", ""))
        role = capitalize_words(request.form.get("role", "")) or "Civilian"
        location = capitalize_words(request.form.get("location", "")) or "Unknown"
        status = request.form.get("status", "Alive")
        age = request.form.get("age", "")
        contact = request.form.get("contact", "")
        emergency = request.form.get("emergency", "")
        description = request.form.get("description", "").strip()
        health_status = capitalize_words(request.form.get("health_status", "Low")) or "Low"
        raw_skills = request.form.get("skills", "")
        skills = [capitalize_words(skill) for skill in raw_skills.split(",") if skill.strip()]

        profiles = load_profiles()
        for profile in profiles:
            if profile["name"].lower() == name.lower():
                return render_template("add_profile.html", editing=False, profile=request.form, message="Name already exists!")

        new_profile = {
            "id": generate_unique_id(),
            "name": name,
            "role": role,
            "skills": skills,
            "location": location,
            "status": status,
            "age": age,
            "contact": contact,
            "emergency": emergency,
            "description": description,
            "health_status": health_status
        }

        profiles.append(new_profile)
        save_profiles(profiles)
        return redirect("/all-profiles")

    return render_template("add_profile.html", editing=False, profile={})

@app.route("/edit-profile/<id>", methods=["GET", "POST"])
def edit_profile(id):
    profiles = load_profiles()
    index = next((i for i, p in enumerate(profiles) if p["id"] == id), None)
    if index is None:
        return "Profile not found", 404

    if request.method == "POST":
        name = capitalize_words(request.form.get("name", ""))
        updated_profile = {
            "id": id,
            "name": name,
            "role": capitalize_words(request.form.get("role", "")) or "Civilian",
            "skills": [capitalize_words(skill) for skill in request.form.get("skills", "").split(",") if skill.strip()],
            "location": capitalize_words(request.form.get("location", "")) or "Unknown",
            "status": request.form.get("status", "Alive"),
            "age": request.form.get("age", ""),
            "contact": request.form.get("contact", ""),
            "emergency": request.form.get("emergency", ""),
            "description": request.form.get("description", "").strip(),
            "health_status": capitalize_words(request.form.get("health_status", "Low")) or "Low"
        }

        for i, p in enumerate(profiles):
            if i != index and p["name"].lower() == name.lower():
                return render_template("add_profile.html", editing=True, profile=request.form, message="Another profile with this name already exists!")

        profiles[index] = updated_profile
        save_profiles(profiles)
        return redirect("/all-profiles")

    profile = profiles[index]
    profile["skills"] = ', '.join(profile.get("skills", []))
    return render_template("add_profile.html", editing=True, profile=profile)

@app.route("/delete-profile/<id>", methods=["POST"])
def delete_profile(id):
    profiles = load_profiles()
    profiles = [p for p in profiles if p["id"] != id]
    save_profiles(profiles)
    return '', 204

@app.route("/profile/<id>")
def profile_details(id):
    profiles = load_profiles()
    profile = next((p for p in profiles if p['id'] == id), None)
    if profile:
        return render_template("profile_details.html", profile=profile)
    return "Profile not found", 404

@app.route("/search", methods=["GET", "POST"])
def search_filter():
    query = request.args.get("query", "").strip().lower()
    role = request.args.get("role", "").strip().lower()
    location = request.args.get("location", "").strip().lower()
    status = request.args.get("status", "").strip()
    health_status = request.args.get('health_status', '')

    profiles = load_profiles()
    results = []
    for p in profiles:
        match = True
        if query and query not in p.get("name", "").lower():
            match = False
        if role and role not in p.get("role", "").lower():
            match = False
        if location and location not in p.get("location", "").lower():
            match = False
        if status and status != p.get("status", ""):
            match = False
        if health_status and health_status != p.get('health_status', ''):
            match = False
        if match:
            results.append(p)

    return render_template("search_filter.html", results=results)

@app.route("/dashboard")
def dashboard():
    profiles = load_profiles()

    status_types = ['Alive', 'Injured', 'Zombie', 'Missing']
    status_counts = {status: 0 for status in status_types}
    for p in profiles:
        status = p.get("status", "Unknown")
        if status in status_counts:
            status_counts[status] += 1

    health_status_levels = ['Low', 'Medium', 'High', 'Critical']
    health_status_counts = {level: 0 for level in health_status_levels}
    for p in profiles:
        health_status = p.get("health_status", "Low")
        if health_status in health_status_counts:
            health_status_counts[health_status] += 1

    return render_template("dashboard.html",
                           total=len(profiles),
                           status_counts=status_counts,
                           health_status_counts=health_status_counts)

# ------------------ Map Routes ------------------

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/get-tags")
def get_tags():
    return jsonify(load_tags())

@app.route("/add-tag", methods=["POST"])
def add_tag():
    data = request.json
    tags = load_tags()

    for t in tags:
        if (
            t["user_id"] == data["user_id"] and
            t["tag"] == data["tag"] and
            abs(t["lat"] - data["lat"]) < 0.0005 and
            abs(t["lng"] - data["lng"]) < 0.0005
        ):
            return jsonify({"message": "You've already tagged this area."}), 400

    new_tag = {
        "id": str(uuid.uuid4()),
        "user_id": data["user_id"],
        "lat": data["lat"],
        "lng": data["lng"],
        "tag": data["tag"],
        "status": "Pending",
        "timestamp": data.get("timestamp") or datetime.utcnow().isoformat(),
        "up": 0,
        "down": 0
    }

    tags.append(new_tag)
    save_tags(tags)
    return jsonify({ **new_tag, "id": new_tag["id"] })

@app.route("/delete-tag/<tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tags = load_tags()
    updated = [t for t in tags if t["id"] != tag_id]
    if len(updated) == len(tags):
        return jsonify({"error": "Tag not found"}), 404
    save_tags(updated)
    return jsonify({"success": True})

@app.route("/vote/<tag_id>/<direction>", methods=["POST"])
def vote(tag_id, direction):
    tags = load_tags()
    for tag in tags:
        if tag["id"] == tag_id:
            if direction == "up":
                tag["up"] += 1
            elif direction == "down":
                tag["down"] += 1
            save_tags(tags)
            return jsonify(tag)
    return jsonify({"error": "Tag not found"}), 404

@app.route("/test-db")
def test_db():
    survivors = Survivor.query.all()
    return jsonify([s.name for s in survivors])

@app.route("/init-db")
def init_db():
    db.create_all()
    return "Database tables created!"



@app.route("/panel")
def panel():
    return render_template("panel.html")

# ------------------ Main ------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
