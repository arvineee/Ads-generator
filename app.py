from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database model ---
class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    hashtags = db.Column(db.String(500), nullable=True)
    ad_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Hooks & CTAs ---
hooks = [
    "🔥 Don’t miss this!",
    "👉 Here’s what you need to know:",
    "✨ A must-read today:",
    "📢 Breaking insight:",
    "💡 Fresh perspective:"
]

call_to_actions = {
    "twitter": ["Read more 👇", "Click & share!", "Your thoughts? 💬"],
    "whatsapp": ["Tap to read 📖", "Forward to your friends 👥", "Check it out now ✅"],
    "facebook": ["Join the discussion!", "Share with your circle 🌍", "Like & comment 💬"],
    "general": ["Read full blog 👉", "Discover more here:", "Learn more 👇"]
}

# --- Generate ad ---
def generate_ad(title, description, platform, hashtags):
    hook = random.choice(hooks)
    cta = random.choice(call_to_actions.get(platform, call_to_actions["general"]))
    return f"{hook}\n\n{title}\n\n{description}\n\n{cta}\n\n{hashtags}"

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    ad = None
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        platform = request.form["platform"]
        hashtags = request.form.get("hashtags", "")
        
        ad = generate_ad(title, description, platform, hashtags)

        # Save to DB
        new_ad = Ad(title=title, description=description, platform=platform, hashtags=hashtags, ad_text=ad)
        db.session.add(new_ad)
        db.session.commit()

    return render_template("index.html", ad=ad)

@app.route("/history", methods=["GET", "POST"])
def history():
    if request.method == "POST":
        # Update hashtags for a specific ad
        ad_id = request.form["ad_id"]
        new_hashtags = request.form["hashtags"]
        ad = Ad.query.get(ad_id)
        if ad:
            ad.hashtags = new_hashtags
            # Update ad_text with new hashtags
            ad.ad_text = generate_ad(ad.title, ad.description, ad.platform, new_hashtags)
            db.session.commit()
    ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return render_template("history.html", ads=ads)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
