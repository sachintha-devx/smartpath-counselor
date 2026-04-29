import os
from groq import Groq
from dotenv import load_dotenv
from db import get_answer, save_knowledge

# 🔥 Gemini
import google.generativeai as genai

# 🔥 Replicate
import replicate

load_dotenv()

# ✅ ENV
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert ICT Educational Counselor.

Always:
- Recommend suitable IT degrees
- Suggest skills needed
- Mention career paths
- Give clear structured answers

If user asks for diagrams:
- Explain clearly
- Structure visually
"""

# 🔍 Detect diagram request
def needs_image(user_input):
    keywords = ["diagram", "flowchart", "visual", "graph", "chart", "show", "image"]
    return any(word in user_input.lower() for word in keywords)

# 🤖 Gemini prompt creator
def generate_image_query(user_input):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"Create short diagram prompt: {user_input}"
        )
        return response.text.strip()
    except:
        return user_input

# 🔁 Fallback keywords
def fallback_query(user_input):
    return user_input + " diagram"

# 🎨 Real image (Replicate)
def generate_real_image(prompt):
    try:
        output = replicate.run(
            "stability-ai/sdxl",
            input={
                "prompt": f"clean educational diagram, {prompt}, labeled",
                "width": 768,
                "height": 512
            }
        )
        return output[0]
    except Exception as e:
        print("Replicate error:", e)
        return None

# 📊 Gemini text diagram
def generate_text_diagram(user_input):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"Create a clean ASCII flowchart diagram for: {user_input}"
        )
        return response.text
    except:
        return "⚠️ Diagram could not be generated."


def get_response(user_input):

    # 🔥 Predefined
    if "best ict degree" in user_input.lower():
        return {"text": "Top ICT degrees: Software Engineering, Data Science, Cyber Security, IT.", "image": None, "diagram": None}

    if "what is ict" in user_input.lower():
        return {"text": "ICT = Information and Communication Technology.", "image": None, "diagram": None}

    # 🔍 DB
    db_answer = get_answer(user_input)
    if db_answer:
        return {"text": "(From DB) " + db_answer, "image": None, "diagram": None}

    # 🤖 AI answer
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    save_knowledge(user_input, reply)

    image_url = None
    diagram_text = None

    if needs_image(user_input):

        try:
            query = generate_image_query(user_input)
        except:
            query = fallback_query(user_input)

        # 1️⃣ Try real image
        image_url = generate_real_image(query)

        # 2️⃣ If failed → Gemini diagram
        if not image_url:
            diagram_text = generate_text_diagram(user_input)

        # 3️⃣ If both fail → fallback image
        if not image_url and not diagram_text:
            image_url = f"https://source.unsplash.com/800x400/?{query.replace(' ', ',')},diagram"

    return {
        "text": reply,
        "image": image_url,
        "diagram": diagram_text
    }