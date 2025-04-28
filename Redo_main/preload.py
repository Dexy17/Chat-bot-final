# print("a")
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz
import numpy as np
# print("Booting up")
# print("b")

model = ""
try:
    print("Loading model from memory")
    model = SentenceTransformer(r"C:\Users\Lenovo\Documents\GitHub\chat-bot\Redo\preload")
except:
    print("Failed to load model from memory, reinstalling...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save(r"C:\Users\Lenovo\Documents\GitHub\chat-bot\Redo\preload")
# print("Booted up")

#list of all symptoms
symptom_list = [
    "Shortness of breath", "Dizziness", "Nausea", "Headache", "Chest pain", "blood pressure / bp","stomachache",
    "Fatigue", "Swelling in the legs or feet", "Stomach cramps", "Back pain",
    "Sore throat", "Rash", "Itchy skin", "Blurry vision", "Ringing in the ears",
    "Sweating", "Chills", "Fainting", "Difficulty swallowing", "Weight loss",
    "Weight gain", "Heart palpitations", "Dry mouth", "Frequent urination",
    "Painful urination", "Blood in urine", "Constipation", "Diarrhea", "Cough",
    "Coughing up blood", "Joint pain", "Numbness", "Tingling sensation",
    "Muscle weakness", "Loss of appetite", "Trouble sleeping",
    "Sleepiness during the day", "Hot flashes", "Feeling cold", "Bruising",
    "Difficulty concentrating", "Memory problems", "Tremors",
    "Cold hands or feet", "Sudden pain in one part of the body",
    "Sensitivity to light", "Sensitivity to sound", "Hoarseness", "Thirst",
    "Dry skin", "Vomiting", "Abdominal pain", "Heartburn", "Gas or bloating",
    "Painful menstruation", "Irregular menstrual cycle", "Weakness",
    "Increased hunger", "Shaking", "Difficulty breathing (general)",
    "Dizziness when standing", "Blackouts", "Feeling faint", "Dry eyes",
    "Difficulty moving limbs", "Skin color changes", "Lump or swelling",
    "Pain when touched", "Anxiety", "Hearing loss", "Bad breath",
    "Excessive saliva", "Changes in bowel habits", "Chest pressure",
    "Gurgling from the stomach", "Throbbing head", "Mental fog",
    "Night sweating", "Coughing up mucus", "Blood in stool", "Leg cramps",
    "Brittle nails", "Swelling around the eyes", "Wound discharge",
    "Uncontrolled movements", "Loss of taste", "Fullness after eating",
    "Red or inflamed skin", "Mouth ulcers", "Heavy periods",
    "Discomfort after eating", "Sensitivity to cold or heat", "Muscle cramps",
    "Choking feeling", "Skin sensitivity to pressure", "Sore eyes",
    "Sudden urge to urinate", "Fever", "Persistent hiccups",
    "Difficulty speaking", "Loss of balance", "Feeling unsteady", "Confusion",
    "Mood swings", "Restlessness", "Irritability", "Changes in vision (general)",
    "Double vision", "Eye pain", "Nosebleeds", "Excessive tearing",
    "Ear pain", "Ear discharge", "Nasal congestion", "Sneezing",
    "Swollen lymph nodes", "Chest tightness", "Rapid heartbeat",
    "Slow heartbeat", "Irregular heartbeat", "Paleness",
    "Yellowing of skin or eyes", "Excessive thirst",
    "Excessive urination (general)", "Joint stiffness", "Muscle stiffness",
    "Muscle spasms", "Paralysis", "Seizures", "Delusions", "Hallucinations",
    "Suicidal thoughts", "Itchy scalp", "Hair loss", "Bleeding gums",
    "Tooth pain", "Difficulty chewing", "Soreness in mouth or tongue",
    "Metallic taste", "Chest burning", "Chest heaviness", "Frequent belching",
    "Passing gas", "Anal itching", "Rectal pain", "Pain during bowel movements",
    "Changes in stool color", "Fecal incontinence", "Difficulty controlling urination",
    "Abnormal vaginal bleeding", "Vaginal discharge", "Pain during intercourse",
    "Erectile dysfunction", "Skin lumps", "Skin lesions", "Excessive dryness (skin)",
    "Oily skin", "Acne", "Skin peeling", "Skin thickening", "Skin scarring",
    "Night blindness", "Sensitivity to glare", "Chronic tearing (eyes)",
    "Eye redness", "Eye discharge", "Vision loss", "Water retention",
    "Decreased urine output", "Swollen hands", "Muscle aches", "Joint swelling",
    "Neck stiffness", "Neck pain", "Throat swelling", "Sore mouth corners",
    "Difficulty opening mouth", "Jaw pain", "Jaw locking", "Tooth sensitivity",
    "Hot flushes", "Excessive hair growth (body or face)", "Body odor (unusual or excessive)",
    "Nipple discharge", "Lump in breast", "Unusual body odor", "Skin cracking",
    "Excessive dandruff", "Brittle hair", "Sensitivity in scalp",
    "Feeling of pressure in the head", "Rapid weight changes",
    "Loose skin (after weight change)", "Stretch marks",
    "Bulging veins in legs or feet", "Pain behind the eyes", "Eye swelling",
    "Burning sensation on skin", "Crawling sensation on skin",
    "Restlessness in legs (general)"
]

#preloading the embedding of all the known symtoms
embedding_symptom = model.encode(symptom_list,convert_to_tensor=True)

# list of all the stuff that needs to be preloaded
