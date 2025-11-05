# mindtrip_app.py
import streamlit as st
import time
import random

# ---------- Page config & style ----------
st.set_page_config(page_title="MindTrip — Tamil Nadu & Nearby", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/minecraft-4');
html, body, [class*="css"] {
    background: linear-gradient(135deg,#071028,#0f2346);
    color: #ffd966;
    font-family: 'Minecraft', sans-serif;
}
h1,h2,h3 { color: #ffd966; }
.stButton>button { background:#ffd966; color:#071028; font-weight:700; border-radius:10px; padding:8px 18px; }
.stTextInput>div>input, .stNumberInput>div>input, textarea, .stSelectbox>div { background:#071933 !important; color:#ffd966 !important; border:1px solid #ffd966 !important; border-radius:8px; }
.chat-box { background:#081b36; padding:10px; border-radius:8px; margin-bottom:8px; }
.user { color:#9ad4ff; font-weight:600; }
.bot { color:#ffd966; font-weight:600; }
.small { color:#b8c7d6; font-size:12px; }
.info-box { background:#071a2a; padding:12px; border-radius:8px; border:1px solid #2a3b55; }
</style>
""", unsafe_allow_html=True)

st.title("🌙 MindTrip — Your AI Travel Companion")
st.write("Personalized, offline-curated travel ideas for Tamil Nadu & nearby places. Chat with the AI buddy on the right.")

# ---------- Session state ----------
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"  # welcome -> loading -> main
if "name" not in st.session_state:
    st.session_state.name = ""
if "age" not in st.session_state:
    st.session_state.age = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None
if "selected_pref" not in st.session_state:
    st.session_state.selected_pref = None
if "selected_sub" not in st.session_state:
    st.session_state.selected_sub = None
if "last_idea" not in st.session_state:
    st.session_state.last_idea = None
if "history" not in st.session_state:
    st.session_state.history = []
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ---------- Built-in data (ideas include an estimated cost in INR) ----------
DATA = {
    "Coimbatore": {
        "Night Out": [
            {"title":"Rooftop dinner & city drive","desc":"Rooftop dinner at That's Y Food, then night drive to Valparai viewpoint.","cost":1200},
            {"title":"Mall + Movie + Dessert","desc":"Brookefields Mall shopping, movie at Prozone, desserts at Cream Centre.","cost":900},
            {"title":"Park walk & café night","desc":"Evening walk at Race Course, dinner & coffee at a cosy café.","cost":700}
        ],
        "Hiking Adventure": [
            {"title":"Velliangiri trek + Siruvani","desc":"Early trek to Velliangiri Hills, cool off at Siruvani Falls.","cost":500},
            {"title":"Dhoni Hills day trip","desc":"Scenic Dhoni Hills trek with picnic and tea stop.","cost":600}
        ],
        "Foodie Hunt": [
            {"title":"South-Indian special tour","desc":"Breakfast at Sree Annapoorna, lunch at Haribhavanam, dinner at Junior Kuppanna.","cost":800},
            {"title":"Street food & sweets","desc":"RS Puram street food crawl, end with Cream Centre desserts.","cost":400}
        ]
    },
    "Chennai": {
        "Sea Food": [
            {"title":"Marina seafood day","desc":"Seafood lunch near Marina, sunset at Elliot's Beach, dinner at The Wharf.","cost":1000},
            {"title":"Fisherman's Cove plan","desc":"Brunch at Fisherman's Cove, evening cafes at Besant Nagar.","cost":1200}
        ],
        "Night Out": [
            {"title":"Mall + rooftop + drive","desc":"Phoenix Marketcity shopping, rooftop dinner, ECR night drive.","cost":1500},
            {"title":"Movie + late dinner","desc":"VR Chennai movie + dinner at Absolute Barbecue.","cost":900}
        ],
        "Cultural Day": [
            {"title":"Temples & museums","desc":"Kapaleeshwarar Temple, museum visit, classical show.", "cost":700}
        ]
    },
    "Kerala": {
        "Beachy Day": [
            {"title":"Kovalam day","desc":"Relax at Kovalam, seafood at The Tides, sunset at Varkala cliff.","cost":1100},
            {"title":"Cherai & Fort Kochi","desc":"Morning at Cherai Beach, Fort Kochi stroll and seafood lunch.","cost":900}
        ],
        "Night Out": [
            {"title":"Houseboat dinner","desc":"Night on a houseboat in Alleppey with candlelight dinner.","cost":3000},
            {"title":"Kochi cafe crawl","desc":"Cafe hopping in Fort Kochi and riverside dinner.","cost":1300}
        ],
        "Hiking Adventure": [
            {"title":"Munnar tea trails","desc":"Tea estate hikes and Echo Point photos.","cost":900}
        ]
    },
    "Bangalore": {
        "Date Night": [
            {"title":"Cubbon Park + rooftop","desc":"Evening walk and dinner at Olive Bar & Kitchen.","cost":1500}
        ],
        "Foodie Hunt": [
            {"title":"CTR + Truffles Tour","desc":"Breakfast at CTR, burgers at Truffles, cafe hopping.","cost":800}
        ],
        "Short Trip": [
            {"title":"Nandi Hills sunrise","desc":"Early drive to Nandi Hills with breakfast at hilltop cafe.","cost":600}
        ]
    },
    "Madurai": {
        "Cultural Day": [
            {"title":"Meenakshi Temple flow","desc":"Temple visit, historic streets, Jigarthanda tasting.","cost":500}
        ],
        "Foodie Hunt": [
            {"title":"Madurai mutton biryani tour","desc":"Try local biryanis and sweets across the city.","cost":600}
        ]
    },
    "Ooty": {
        "Photography Tour": [
            {"title":"Doddabetta + Botanical Gardens","desc":"Sunrise shots and botanical garden strolls.","cost":700}
        ]
    },
    "Kodaikanal": {
        "Hill Escape": [
            {"title":"Lake boating & Coaker's Walk","desc":"Relaxed boating and sunrise viewpoint.","cost":800}
        ]
    },
    "Pondicherry": {
        "Beach & Cafe": [
            {"title":"French Quarter & Promenade","desc":"Cycle tour, seaside cafe lunch, Rock Beach sunset.","cost":900}
        ]
    }
}

# ---------- Preference -> dynamic suboptions mapping ----------
SUBOPTIONS = {
    "Foodie Hunt": ["Veg", "Non-Veg", "Seafood", "Local Cuisine"],
    "Hiking Adventure": ["Hill Climb", "Waterfall Trek", "Forest Trail"],
    "Date Night": ["Cafe", "Lake View", "Rooftop"],
    "Photography Tour": ["Sunrise", "Architecture", "Nature"],
    "Night Out": ["Rooftop", "Mall+Movie", "Beach Drive"],
    "Beachy Day": ["Relax & Swim", "Seafood Lunch", "Water Sports"],
    "Peaceful Retreat": ["Ayurveda Spa", "Houseboat", "Hill Cottage"]
}

# ---------- Helpers ----------
def find_city_key(user_text):
    """Loose match: check if any known city is substring of user_text or vice-versa."""
    if not user_text: 
        return None
    u = user_text.strip().lower()
    for city in DATA.keys():
        if city.lower() == u or city.lower() in u or u in city.lower():
            return city
    return None

def pick_idea(city, pref, subpref=None):
    """Return an idea dict matching city+pref optionally filtered by subpref (subpref not strictly used here)."""
    city_data = DATA.get(city, {})
    ideas = city_data.get(pref, [])
    if not ideas:
        # fallback: grab any idea from the city
        lists = sum((v for v in city_data.values()), [])
        ideas = lists if lists else []
    if not ideas:
        # global fallback
        all_ideas = sum((sum((v for v in DATA[c].values()), [] ) for c in DATA.keys()), [])
        return random.choice(all_ideas) if all_ideas else {"title":"No idea","desc":"No data","cost":0}
    return random.choice(ideas)

def format_idea_card(idea):
    return f"**{idea['title']}**\n\n{idea['desc']}\n\n**Estimated cost:** ₹{idea['cost']}"

# ---------- UI: Welcome ----------
if st.session_state.stage == "welcome":
    st.header("Welcome to MindTrip ✨")
    st.write("Tell us a bit about yourself and we'll read your vibe to suggest curated ideas.")
    name = st.text_input("Your name", value=st.session_state.name)
    age = st.number_input("Your age", min_value=10, max_value=120, value=(st.session_state.age or 20))
    if st.button("Get Started"):
        if not name.strip():
            st.error("Please enter your name.")
        else:
            st.session_state.name = name.strip()
            st.session_state.age = age
            st.session_state.stage = "loading"
            st.session_state.conversation.append(("AI", f"Hi {st.session_state.name}! I'm MindTrip — your travel buddy."))
            st.rerun()

# ---------- Loading (10s) ----------
elif st.session_state.stage == "loading":
    st.header(f"Let's generate your go-to ideas, {st.session_state.name}!")
    st.info("MindTrip is thinking... sit tight for a moment.")
    with st.spinner("Generating your curated ideas..."):
        time.sleep(10)
    st.session_state.stage = "main"
    st.rerun()

# ---------- Main UI ----------
elif st.session_state.stage == "main":
    left, right = st.columns([3,1], gap="large")

    # ---- Left: inputs & idea output ----
    with left:
        st.subheader(f"Hello {st.session_state.name} — type your destination and choose preferences")
        dest_text = st.text_input("Type destination (e.g., Coimbatore, Chennai, Kerala, Bangalore, Madurai, Ooty...)")
        pref = st.selectbox("Choose a main preference", list(SUBOPTIONS.keys()))
        subpref = None
        if pref in SUBOPTIONS:
            subpref = st.selectbox("Choose a sub-option", ["Any"] + SUBOPTIONS[pref])
        budget = st.number_input("Enter your budget (₹)", min_value=0, value=1000, step=100)
        days = st.number_input("How many days?", min_value=1, max_value=15, value=2)

        if st.button("Generate Idea"):
            if not dest_text.strip():
                st.warning("Please type a destination name first.")
            else:
                matched = find_city_key(dest_text)
                if not matched:
                    st.info("Destination not in curated list — I'll pick similar popular places for ideas.")
                    matched = random.choice(list(DATA.keys()))
                idea = pick_idea(matched, pref)
                st.session_state.last_idea = {"city": matched, "pref": pref, "subpref": subpref, "idea": idea, "budget": budget, "days": days}
                st.session_state.history.append(st.session_state.last_idea.copy())
                st.markdown("---")
                st.markdown(f"### ✨ Suggestion for {matched} — *{pref} / {subpref if subpref else 'Any'}*")
                st.info(format_idea_card(idea))
                # suggestion vs budget note
                if idea.get("cost", 0) > budget:
                    st.warning(f"Estimated cost ₹{idea['cost']} exceeds your budget ₹{budget}. Consider altering or raising budget.")
                else:
                    st.success("This fits your budget ✅")

    # ---- Right: AI chat ----
    with right:
        st.subheader("🤖 MindTrip — AI Companion")
        st.markdown('<div class="small">Chat with the AI buddy. Try: "hi", name a place (Coimbatore), say a mood (Night Out), or say "alter".</div>', unsafe_allow_html=True)
        # show conversation
        for speaker, msg in st.session_state.conversation[-8:]:
            if speaker == "AI":
                st.markdown(f"<div class='chat-box bot'><b>MindTrip:</b> {msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-box user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)

        user_msg = st.text_input("Message to MindTrip", key="chat_input")
        if st.button("Send", key="send_btn"):
            txt = user_msg.strip()
            if not txt:
                st.warning("Type a message to chat.")
            else:
                st.session_state.conversation.append(("User", txt))
                lower = txt.lower()
                responded = False

                # greetings
                if any(g in lower for g in ["hi", "hello", "hey"]):
                    st.session_state.conversation.append(("AI", f"Hey {st.session_state.name}! 👋 Where would you like to go?"))
                    responded = True

                # user mentions city
                for city in DATA.keys():
                    if city.lower() in lower:
                        st.session_state.selected_city = city
                        opts = ", ".join(DATA[city].keys())
                        st.session_state.conversation.append(("AI", f"Great — {city}! Which vibe do you want? Options: {opts}"))
                        responded = True
                        break

                # user mentions pref mood while a selected city exists
                if not responded and st.session_state.get("selected_city"):
                    for mood in DATA[st.session_state.selected_city].keys():
                        if mood.lower() in lower:
                            idea = pick_idea(st.session_state.selected_city, mood)
                            st.session_state.last_idea = {"city": st.session_state.selected_city, "pref": mood, "idea": idea}
                            st.session_state.history.append(st.session_state.last_idea.copy())
                            st.session_state.conversation.append(("AI", f"Here's an idea for {mood} in {st.session_state.selected_city}:"))
                            st.session_state.conversation.append(("AI", f"{idea['title']} — {idea['desc']} (Est ₹{idea['cost']})"))
                            st.session_state.conversation.append(("AI", "Do you like this idea, or should I alter it?"))
                            responded = True
                            break

                # alter / change
                if not responded and any(k in lower for k in ["alter", "change", "another", "no"]):
                    if st.session_state.last_idea:
                        city = st.session_state.last_idea["city"]
                        pref = st.session_state.last_idea["pref"]
                        alt_candidates = [x for x in DATA[city][pref] if x != st.session_state.last_idea["idea"]]
                        if not alt_candidates:
                            alt_candidates = DATA[city][pref]
                        new = random.choice(alt_candidates)
                        st.session_state.last_idea = {"city": city, "pref": pref, "idea": new}
                        st.session_state.history.append(st.session_state.last_idea.copy())
                        st.session_state.conversation.append(("AI", "Okay — here's another idea:"))
                        st.session_state.conversation.append(("AI", f"{new['title']} — {new['desc']} (Est ₹{new['cost']})"))
                        st.session_state.conversation.append(("AI", "Do you like this one?"))
                        responded = True
                    else:
                        st.session_state.conversation.append(("AI", "I don't have a previous idea to alter yet. Tell me a place first."))
                        responded = True

                # confirmation
                if not responded and any(k in lower for k in ["yes", "love", "like", "perfect"]):
                    st.session_state.conversation.append(("AI", "Fantastic! Would you like me to save this idea or generate another?"))
                    responded = True

                # direct generate request e.g., "generate chennai night out"
                if not responded and ("generate" in lower or "suggest" in lower or "plan" in lower):
                    found_city = None
                    for city in DATA.keys():
                        if city.lower() in lower:
                            found_city = city
                            break
                    found_pref = None
                    if found_city:
                        for mood in DATA[found_city].keys():
                            if mood.lower() in lower:
                                found_pref = mood
                                break
                    if found_city and found_pref:
                        idea = pick_idea(found_city, found_pref)
                        st.session_state.last_idea = {"city": found_city, "pref": found_pref, "idea": idea}
                        st.session_state.history.append(st.session_state.last_idea.copy())
                        st.session_state.conversation.append(("AI", f"Generated for {found_city} ({found_pref}):"))
                        st.session_state.conversation.append(("AI", f"{idea['title']} — {idea['desc']} (Est ₹{idea['cost']})"))
                        st.session_state.conversation.append(("AI", "Do you want me to alter it or is it good?"))
                        responded = True

                if not responded:
                    st.session_state.conversation.append(("AI", "Sorry, I didn't catch that. Try: 'hi', name a place (Coimbatore), or say a mood like 'Night Out'."))

                st.rerun()

# ---------- History section ----------
st.markdown("---")
st.subheader("Recent ideas (this session)")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-6:]), 1):
        st.markdown(f"**{i}. {item['city']} — {item['pref']}**")
        idea = item["idea"]
        st.write(f"{idea['title']} — {idea['desc']} (Est ₹{idea['cost']})")
else:
    st.write("No ideas generated yet. Start with a place and preference.")
