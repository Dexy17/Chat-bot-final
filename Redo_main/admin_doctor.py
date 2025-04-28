print("Booting up")
from imp_funcs import *
import user_login
# import report_gen as rg
class patient_record:
    pass



if __name__ == "__main__":
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Booted up")
    while(True):
        op = input('''Admin/Doctor login:(d for doctor login)''')
        if op.lower() == "admin!":
            user_login.admin_login()
        elif op.lower() in ["d","doctor"]:
            user_login.doc_login()
        elif op.lower() in ["yes","y","yah"]:
            pass
        elif op.lower() in ["no","n"]:
            pass
        elif op.lower() in ["q","quit"]:
            break
