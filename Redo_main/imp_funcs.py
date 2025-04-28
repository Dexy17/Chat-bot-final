from preload import *
# from logger import * # this is imported through preload
def semantic_similarity(text1,text2,prt = False):
    if isinstance(text2, str):
        text2 = [text2]
    if isinstance(text1, str):
        text1 = [text1]
    embeddingA = model.encode(text1)
    embeddingB = model.encode(text2)
    similarity = 0
    for i in range(0,len(text2)):
        similarity = max(cosine_similarity([embeddingA[0]], [embeddingB[i]]),similarity)
        if(prt == True):
            print(text1[0],text2[i],(similarity))
    return float(similarity[0][0])

def fuzzy_match(word1, word2):
    return fuzz.ratio(word1, word2)

if __name__ == "__main__":
    # text1 = ["Y","N","YES","no","nah"]
    # text2 = ["yes","y","no","n"]
    # for i in text1:
    #     semantic_similarity(i,text2,True)

    # embeddings = model.encode(["yes","no"])
    # for i in text1:
    #     for j in text2:
    #         print(i,j,fuzzy_match(i,j))
    # embeddingB = model.encode(text2)
    print(semantic_similarity("pain in my head","headache"))

# if __name__ == "__main__":