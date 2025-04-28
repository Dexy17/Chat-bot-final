from chat_gui import ChatApp
from imp_funcs import *
import config
from datetime import datetime
from user_login import *
import time
from sentence_to_symptom import get_symptoms, is_exit_command
def run_my_logic(app):
    while True:
        # app.reset_chat()
        op = app.ask_user_direct('''Hi, This is the Medical assistant chatbot which is here to streamline the 
    medical process and save your time!

    Is this your first time at the hospital? (y/n)
    ''')
        print(op)
        if op.lower() == "q":
            break

        elif op.lower() in ["d", "doctor"]:
            pass

        elif op.lower() in ["yes", "y", "yah"]:
            # Begin new patient registration
            username = app.ask_user_direct("Choose a username (for future logins):").lower()
            while users_col.find_one({"username": username}):
                app._add_bot_message("That username already exists. Please choose another username.")
                username = app.ask_user_direct("Please choose another username:").lower()

            email = app.ask_user_direct("Enter your email address:")
            password = app.ask_password("Set a password (input will be hidden):")
            password2 = app.ask_password("Confirm your password:")
            while password != password2:
                app._add_bot_message("Passwords do not match. Please try again.")
                password = app.ask_password("Set a password:")
                password2 = app.ask_password("Confirm your password:")

            name = app.ask_user_direct("Full Name:")
            age = app.ask_user_direct("What is your age? (give simple numbers like 15)")
            while not age.isdigit():
                age = app.ask_user_direct("Please enter a valid number for age:")
            age = int(age)

            gender = "K"
            while gender.lower() not in ['m', 'f', 'o', 'r']:
                gender = app.ask_user_direct(
                    '''Please input:\nM: Male\nF: Female\nO: Other\nR: Rather not say'''    
                ).lower()
            if(gender == 'm'):
                gender = "Male"
            elif(gender == 'f'):
                gender = "Female"
            contact = app.ask_user_direct("Enter your phone number:")
            enc_contact = encrypt_contact(contact)

            # Core medical history free-text
            history = app.ask_user_dynamic(
                "Do you have any previous medical history we should be aware of? Describe briefly or type 'none'."
            )

            # Additional structured medical info
            medical_info = {}
            medical_info['Major_Surgeries'] = app.ask_user_dynamic(
                "Have you had any major surgeries? If yes, list them; otherwise type 'none'."
            )
            medical_info['Chronic_Conditions'] = app.ask_user_dynamic(
                "Do you have any chronic conditions (e.g., diabetes, hypertension)? List or 'none'."
            )
            medical_info['Allergies'] = app.ask_user_dynamic(
                "List any known allergies (medications, food, etc.) or 'none'."
            )
            medical_info['Smoking_Status'] = app.ask_user_dynamic(
                "Do you smoke? (yes/no)")
            medical_info['Alcohol_Use'] = app.ask_user_dynamic(
                "Do you consume alcohol? (yes/no)")

            # Collect symptom data via NLP loop
            symptoms = []
            added_symptoms = set()
            add_symptom = app.ask_user_dynamic(
                "Now, please describe your symptoms in simple language (type 'bye' to finish)."
            )
            print(type(add_symptom), "Type of add symptom!")
            print("Add symptom:" ,add_symptom)
            add_symptom = str(add_symptom)
            while is_exit_command(add_symptom.lower()) == False:
                print("ss.symptom list",get_symptoms(add_symptom))
                detected = get_symptoms(add_symptom)
                if(len(detected) == 0):
                    app.prt_bot(f"I am sorry I could not find any symptoms in the above and i have logged this case")
                for symptom in detected:
                    if symptom in added_symptoms:
                        continue
                    print("The code reached line 87 once!")
                    app._add_bot_message(f"Detected symptom: {symptom}")

                    freq = app.ask_user(
                        "How frequently does this symptom occur? (e.g., daily, occasionally; '0' if not present)"
                    )
                    if freq.strip() == '0':
                        app._add_bot_message(f"Skipping {symptom}.")
                        continue
                    while not freq:
                        freq = app.ask_user("Please provide a valid frequency:")

                    sev = app.ask_user("On a scale of 1 to 10, how severe is this symptom?")
                    while not sev.isdigit() or not (1 <= int(sev) <= 10):
                        sev = app.ask_user("Enter a number between 1 and 10 for severity:")

                    duration = app.ask_user(
                        "How long have you experienced this symptom? (e.g., 2 days, 1 week)"
                    )
                    while not duration:
                        duration = app.ask_user("Please provide a valid duration:")

                    notes = app.ask_user("Any additional notes about this symptom?")
                    date_str = datetime.now().strftime("%Y-%m-%d")

                    symptoms.append({
                        "Symptom": symptom,
                        "Frequency": freq,
                        "Severity": sev,
                        "Duration": duration,
                        "Additional_Notes": notes,
                        "Date": date_str
                    })
                    added_symptoms.add(symptom)
                add_symptom = app.ask_user_dynamic(
                    "Describe more symptoms or type 'bye' to finish."
                )
                add_symptom = str(add_symptom)

            # Insert new patient record
            users_col.insert_one({
                "username": username,
                "Name": name,
                "email": email,
                "password": hash_password(password),
                "role": "patient"
            })
            patients_col.insert_one({
                "patient_id": username,
                "demographic_data": {
                    "Name": name,
                    "Age": age,
                    "Gender": gender,
                    "Contact": enc_contact
                },
                "medical_history": history,
                "medical_info": medical_info,
                "symptoms_data": symptoms,
                "doctor_notes": []
            })

            app._add_bot_message(
                f"Thank you {name}, you have been successfully registered with ID: {username}"
            )
        elif op.lower() in ["no", "n"]:
            app._add_bot_message("Welcome back! Let's log you in.")
            username = app.ask_user("Enter your username:").lower()
            password = app.ask_password("Enter your password:")

            user = users_col.find_one({"username": username})
            if not user or not verify_password(password, user["password"]):
                app._add_bot_message("Invalid credentials. Please restart.")
                # app.reset_chat()
                continue

            patient = patients_col.find_one({"patient_id": username})
            today = datetime.now().strftime("%Y-%m-%d")

            old_symptoms = patient.get("symptoms_data", [])
            to_move = [s for s in old_symptoms if s.get("Date") != today]
            keep_today = [s for s in old_symptoms if s.get("Date") == today]

            if to_move:
                history = patient.get("medical_history", [])
                if isinstance(history, str):
                    history = []
                history.extend(to_move)
                patients_col.update_one({"patient_id": username}, {
                    "$set": {
                        "symptoms_data": keep_today,
                        "medical_history": history
                    }
                })

            symptoms = keep_today[:]
            added_symptoms = set(s["Symptom"] for s in symptoms)
            add_symptom = app.ask_user("Now, please describe your symptoms in simple language")
            while is_exit_command(add_symptom.lower()) == False:
                symptoms_ls = get_symptoms(add_symptom)
                if(len(symptoms_ls) == 0):
                    app.prt_bot(f"I am sorry I could not find any symptoms in the above and i have logged this case")
                for i in symptoms_ls:
                    if i in added_symptoms:
                        # app._add_bot_message("This symptom has already been added. Please enter a new one.")
                        # add_symptom = app.ask_user("Add another symptom? (y/n)")
                        continue
                    
                    app.prt_bot(f"I have detected the symptom {i}")

                    frequency = app.ask_user("How frequently does this symptom occur? (e.g., daily, occasionally) (please type '0' in case you are not feeling this symptom)")
                    if frequency.strip("'") == '0':
                        app.prt_bot(f"Deleting symptom {i}")
                        continue

                    # adding the symptom if user confirms it                                       
                    added_symptoms.add(i)

                    while frequency.strip() == "":
                        frequency = app.ask_user("Please provide a valid frequency:")

                    severity = app.ask_user("On a scale of 1 to 10, how severe is this symptom?")
                    while not severity.isdigit() or not (1 <= int(severity) <= 10):
                        severity = app.ask_user("Please enter a number between 1 and 10 for severity:")

                    duration = app.ask_user("For how long have you been experiencing this symptom? (e.g., 2 days, 1 week)")
                    while duration.strip() == "":
                        duration = app.ask_user("Please provide a valid duration:")

                    notes = app.ask_user("Any additional notes you'd like to add?")
                    date_str = datetime.now().strftime("%Y-%m-%d")

                    symptoms.append({
                        "Symptom": i,
                        "Frequency": frequency,
                        "Severity": severity,
                        "Duration": duration,
                        "Additional_Notes": notes,
                        "Date": date_str
                    })
                    # added_symptoms.add(symptom)
                add_symptom = app.ask_user("Please describe your symptoms: (or just say bye to exit)")
            patients_col.update_one({"patient_id": username}, {"$set": {"symptoms_data": symptoms}})
            app._add_bot_message("Your symptoms have been updated. Thank you!")
        app.update()
        time.sleep(5)
        app.reset_chat()
    app.quit()
    app.destroy()
if __name__ == "__main__":
    app = ChatApp(logic=run_my_logic)
    app.after(300, lambda: run_my_logic(app))
    app.geometry("1366x768")
    app.mainloop()
