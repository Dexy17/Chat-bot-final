from imp_funcs import * 
import logger
def create_list_for_symptoms(s): #takes in a string s as function input and then returns a list with comma seperated potential symtoms for matching.
    ls = []
    try:
        import api_handler as ah
        api_class = ah.GeminiAPIHandler("AIzaSyBkRDmEdtVhVtHHbfvpetHKANTz1EW1qYQ")
        ls = api_class.extract_symptoms(s)
        return ls
    except:
        # print("Gemini failed, going to fallback")
        logger.log_error(f"Gemini Failed to load", exc_info=True)
        a = s.split()
        n = len(a)
        ap = ""
        for i in range(n):
            for j in range(n-i):
                for k in range(i+1):
                    ap += a[j+k] + " "
                ls.append(ap)
                ap = ""
        return ls
    
def get_symptoms(s):
    ls = create_list_for_symptoms(s)
    print("Test of get_symptoms:",s,ls)
    rt = set()
    if(len(ls) == 0 or ls[0] == 'no'):
        print("the s that should be logged is:")
        logger.symptom_logger.debug("----"+s)
        return []
    else:
        for i in ls: # i is a string
            tmp = 0
            rt_pre = ""
            present = False
            embeddingA = model.encode(i)
            for j in range(len(embedding_symptom)):
                similarity = float(cosine_similarity(np.array(embeddingA).reshape(1, -1),
                                     np.array(embedding_symptom[j]).reshape(1, -1)))
                if(similarity > 0.70):
                    present = True
                    if(similarity > tmp):
                        rt_pre = (symptom_list[j])
                        tmp = similarity

                    
            if(present == False):
                logger.symptom_logger.debug(i)
            else:
                rt.add(rt_pre)
    return list(rt)

def is_exit_command(s):
    print("s is reaching here! and s is:", s)
    s = s.lower()
    if s in ["bye","cya","thank you","no","quit","q"]:
        return True
    try:
        import api_handler as ah
        api_class = ah.GeminiAPIHandler("AIzaSyBkRDmEdtVhVtHHbfvpetHKANTz1EW1qYQ")
        return api_class.is_exit_command_ga()

    except:
        print("gemini exit command part failed")
        return False
    
if __name__ == "__main__":
    print(get_symptoms("Hi, this is a test"))