print("Booting up")
from imp_funcs import *

class patient_record:
    pass



if __name__ == "__main__":
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Booted up")
    while(True):
        op = input('''Hi, This is the Medical assistant chatbot which is here to streamline the 
medical process and save your time!

Is this your first time at the hospital? (y/n)''')
        if op.lower() == "admin!":
            pass
        elif op.lower() in ["d","doctor"]:
            pass
        elif op.lower() in ["yes","y","yah"]:
            pass
        elif op.lower() in ["no","n"]:
            pass
        break
