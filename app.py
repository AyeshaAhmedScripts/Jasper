from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import uuid
import json

import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret-key"

# PostgreSQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Goldenmaknae7@103.235.78.133:5432/jasper1'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ Database Models ------------------
class Survivor(db.Model):
    __tablename__ = 'survivors'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    skills = db.Column(db.Text)
    location = db.Column(db.String(100))
    status = db.Column(db.String(30))
    health_status = db.Column(db.String(30))
    age = db.Column(db.Integer)
    contact = db.Column(db.String(30))
    emergency = db.Column(db.String(50))
    description = db.Column(db.Text)
    tags = db.relationship("MapTag", backref="survivor", lazy=True)


class MapTag(db.Model):
    __tablename__ = 'map_tags'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('survivors.id'))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    tag = db.Column(db.String(100))
    status = db.Column(db.String(30))
    timestamp = db.Column(db.BigInteger)
    up = db.Column(db.Integer, default=0)
    down = db.Column(db.Integer, default=0)


# ------------------ Helpers ------------------
def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.strip().split())

def generate_unique_id():
    return str(uuid.uuid4())


# ------------------ Profile Routes ------------------
@app.route("/profiles")
def get_profiles():
    profiles = Survivor.query.all()
    return jsonify([{c.name: getattr(p, c.name) for c in Survivor.__table__.columns} for p in profiles])


@app.route("/all-profiles")
def all_profiles():
    sort_by = request.args.get('sort_by', 'name')
    if sort_by not in ['name', 'status', 'role']:
        sort_by = 'name'
    profiles = Survivor.query.order_by(getattr(Survivor, sort_by).asc()).all()
    return render_template("all_profiles.html", profiles=profiles)


@app.route("/profile-details/<id>")
def profile_details(id):
    profile = Survivor.query.get(id)
    if profile:
        return render_template("profile_details.html", profile=profile)
    flash("Profile not found.", "error")
    return redirect(url_for('all_profiles'))


@app.route("/add-profile", methods=["GET", "POST"])
def add_profile():
    if request.method == "POST":
        name = capitalize_words(request.form.get("name", ""))
        if Survivor.query.filter(db.func.lower(Survivor.name) == name.lower()).first():
            return render_template("add_profile.html", editing=False, profile=request.form, message="Name already exists!")

        age = request.form.get("age", "")
        age = int(age) if age and age.isdigit() else None

        new_profile = Survivor(
            id=generate_unique_id(),
            name=name,
            role=capitalize_words(request.form.get("role", "")) or "Civilian",
            skills=', '.join([capitalize_words(s) for s in request.form.get("skills", "").split(",") if s.strip()]),
            location=capitalize_words(request.form.get("location", "")) or "Unknown",
            status=request.form.get("status", "Alive"),
            age=age,
            contact=request.form.get("contact", ""),
            emergency=request.form.get("emergency", ""),
            description=request.form.get("description", "").strip(),
            health_status=capitalize_words(request.form.get("health_status", "Low")) or "Low"
        )
        db.session.add(new_profile)
        db.session.commit()
        return redirect("/all-profiles")

    return render_template("add_profile.html", editing=False, profile={})


@app.route("/edit-profile/<id>", methods=["GET", "POST"])
def edit_profile(id):
    profile = Survivor.query.get(id)
    if not profile:
        return "Profile not found", 404

    if request.method == "POST":
        name = capitalize_words(request.form.get("name", ""))
        existing = Survivor.query.filter(db.func.lower(Survivor.name) == name.lower(), Survivor.id != id).first()
        if existing:
            return render_template("add_profile.html", editing=True, profile=request.form, message="Name already taken")

        profile.name = name
        profile.role = capitalize_words(request.form.get("role", "")) or "Civilian"
        profile.skills = ', '.join([capitalize_words(s) for s in request.form.get("skills", "").split(",") if s.strip()])
        profile.location = capitalize_words(request.form.get("location", "")) or "Unknown"
        profile.status = request.form.get("status", "Alive")
        
        age = request.form.get("age", "")
        profile.age = int(age) if age and age.isdigit() else None

        profile.contact = request.form.get("contact", "")
        profile.emergency = request.form.get("emergency", "")
        profile.description = request.form.get("description", "").strip()
        profile.health_status = capitalize_words(request.form.get("health_status", "Low")) or "Low"
        db.session.commit()
        return redirect("/all-profiles")

    profile.skills = profile.skills or ""
    return render_template("add_profile.html", editing=True, profile={
        'id': profile.id,
        'name': profile.name,
        'role': profile.role,
        'skills': profile.skills,
        'location': profile.location,
        'status': profile.status,
        'health_status': profile.health_status,
        'age': profile.age,
        'contact': profile.contact,
        'emergency': profile.emergency,
        'description': profile.description
    })


@app.route("/delete-profile/<id>", methods=["POST"])
def delete_profile(id):
    profile = Survivor.query.get(id)
    if profile:
        db.session.delete(profile)
        db.session.commit()
    return '', 204


@app.route("/search")
def search_filter():
    q = request.args
    query = Survivor.query

    if q.get("query"):
        query = query.filter(Survivor.name.ilike(f"%{q.get('query')}%"))
    if q.get("role"):
        query = query.filter(Survivor.role.ilike(f"%{q.get('role')}%"))
    if q.get("location"):
        query = query.filter(Survivor.location.ilike(f"%{q.get('location')}%"))
    if q.get("status"):
        query = query.filter(Survivor.status == q.get("status"))
    if q.get("health_status"):
        query = query.filter(Survivor.health_status == q.get("health_status"))

    results = query.all()
    return render_template("search_filter.html", results=results)


@app.route("/dashboard")
def dashboard():
    profiles = Survivor.query.all()
    status_types = ['Alive', 'Injured', 'Zombie', 'Missing']
    status_counts = {s: 0 for s in status_types}
    for p in profiles:
        if p.status in status_counts:
            status_counts[p.status] += 1

    health_levels = ['Low', 'Medium', 'High', 'Critical']
    health_status_counts = {h: 0 for h in health_levels}
    for p in profiles:
        if p.health_status in health_status_counts:
            health_status_counts[p.health_status] += 1

    return render_template("dashboard.html", total=len(profiles), status_counts=status_counts, health_status_counts=health_status_counts)


# ------------------ Map Routes ------------------
@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/get-tags")
def get_tags():
    tags = MapTag.query.all()
    return jsonify([{c.name: getattr(t, c.name) for c in MapTag.__table__.columns} for t in tags])


@app.route("/add-tag", methods=["POST"])
def add_tag():
    data = request.json
    existing = MapTag.query.filter_by(user_id=data["user_id"], tag=data["tag"]).all()
    for t in existing:
        if abs(t.lat - data["lat"]) < 0.0005 and abs(t.lng - data["lng"]) < 0.0005:
            return jsonify({"message": "You've already tagged this area."}), 400

    new_tag = MapTag(
        id=generate_unique_id(),
        user_id=data["user_id"],
        lat=data["lat"],
        lng=data["lng"],
        tag=data["tag"],
        status="Pending",
        timestamp=data.get("timestamp", int(datetime.utcnow().timestamp() * 1000)),
        up=0,
        down=0
    )
    db.session.add(new_tag)
    db.session.commit()
    return jsonify({c.name: getattr(new_tag, c.name) for c in MapTag.__table__.columns})


@app.route("/delete-tag/<tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tag = MapTag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/vote/<tag_id>/<direction>", methods=["POST"])
def vote(tag_id, direction):
    tag = MapTag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    if direction == "up":
        tag.up += 1
    elif direction == "down":
        tag.down += 1
    db.session.commit()
    return jsonify({c.name: getattr(tag, c.name) for c in MapTag.__table__.columns})


@app.route("/init-db")
def init_db():
    db.create_all()
    return "Database tables created!"


@app.route("/panel")
def panel():
    return render_template("panel.html")

@app.route("/")
def ai_front():
    return render_template("ai_front.html")

# Jasper: Get AI tip (search in JSON)
@app.route('/jasper_reply', methods=['POST'])
def jasper_reply():
    data = request.get_json()
    message = data.get("message", "").lower()

    # Load your jasper_data.json once outside this function for performance
    with open('static/data/jasper_data.json') as f:
        jasper_data = json.load(f)

    reply = "No tips found for your query. Try using different keywords."

    for category in jasper_data["categories"]:
        # Check if any keyword in this category matches the message
        if any(keyword.lower() in message for keyword in category.get("keywords", [])):
            reply = "\n\n".join(category.get("responses", []))
            break

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
