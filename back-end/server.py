#Import Flask
from flask import Flask;

#Generator matrix for the [23, 12, 7] binary Golay code
#Formed by removing one coordinate from the generator matrix of the extended binary Golay code
BINARY_GOLAY_GENERATOR_MATRIX = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
]

#Generator matrix for the [24, 12, 8] extended binary Golay code
EXTENDED_BINARY_GOLAY_GENERATOR_MATRIX = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1]
]

#TODO: Fill out the generator matrix
TERNARY_GOLAY_GENERATOR_MATRIX = []

#TODO: Fill out the generator matrix
EXTENDED_TERNARY_GOLAY_GENERATOR_MATRIX = []

#This function generates a list of all code words by linearly combining all elements of the
#generator matrix
def generate_all_code_words(generator_matrix, base):
    #We know that the elements of the generator matrix are code words
    code_words = generator_matrix.copy()
    
    #We continue until all code words are added
    while True:
        #Flag value for whether or not a code word was added on this iteration
        code_word_added = False

        #Loop through each element of the generator matrix
        for i in range(len(generator_matrix)):
            #Then loop through each element already added to the code
            for j in range(len(code_words)):
                #Allocate memory for a new code word
                code_word = []

                #Add the element of the generator matrix to a code word that has already been
                #added to the code
                for k in range(len(generator_matrix[i])):
                    code_word.append((generator_matrix[i][k] + code_words[j][k]) % base)
                
                #If the sum of the two code words has not already been added, add it.  Since a
                #new code word was added, we expect there may be more code words to account for
                #so we keep iterating
                if code_word not in code_words:
                    code_words.append(code_word)
                    code_word_added = True
        
        #If by the time we have looped through the entire generator matrix we find that we have
        #not added a new code word, we know for sure that we have found all linear combinations
        #of the rows of the generator matrix (i.e. the entire code).
        if not(code_word_added):
            break

    #After we generate the entire code, return it as a list
    return code_words

#TODO: Hamming distance function

#TODO: Generate all code words for all codes and save to memory

#Initialize the Flask application
server = Flask(__name__)

#TODO: Write the binary golay encoding function
@server.route("/binary/encode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/binary/decode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/extended-binary/encode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/extended-binary/decode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/ternary/encode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/ternary/decode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/extended-ternary/encode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the binary golay encoding function
@server.route("/extended-ternary/decode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }