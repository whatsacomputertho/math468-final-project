#Import dependencies
from flask import Flask, request
from flask_cors import CORS, cross_origin
import numpy

#Print the fact that the script is being run
print("Server initializing...", flush=True)

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

#If two vectors are different lengths, this returns the two vectors with the same length, but with
#the shorter vector having zeros appended to the front of it (i.e. its algebraic properties are the
#same).
def fix_vector_lengths(vec1, vec2):
    #Instantiate the return "list of lists"
    vecs = []

    #Check if the vectors lengths are different
    vec1_longer = False
    len_diff = 0
    if len(vec1) > len(vec2):
        vec1_longer = True
        len_diff = len(vec1) - len(vec2)
    if len(vec2) > len(vec1):
        len_diff = len(vec2) - len(vec1)
    
    #If they are, then append zeroes to the beginning of the shorter vector
    if len_diff != 0 and vec1_longer:
        for i in range(len_diff):
            vec2.insert(0, 0)
    elif len_diff != 0 and not(vec1_longer):
        for i in range(len_diff):
            vec2.insert(0, 0)
    
    #Return the list containing the fixed vec 1 and vec 2
    vecs.append(vec1)
    vecs.append(vec2)
    return vecs

#This function adds two vectors together according to addition in the finite field of the given base
def vector_addition(vec1, vec2, base):
    #Instantiate the sum vector
    vec = []

    #Fix the vector lengths (if different lengths)
    vecs = fix_vector_lengths(vec1, vec2)
    
    #Add as usual
    for i in range(len(vecs[0])):
        vec.append((vecs[0][i] + vecs[1][i]) % base)

    #Return the sum
    return vec

#This function calculates the Hamming distance between two vectors
def hamming_distance(vec1, vec2):
    #Instantiate the distance
    dist = 0

    #Fix the vector lengths (if different lengths)
    vecs = fix_vector_lengths(vec1, vec2)

    #Calculate hamming distance as usual
    for i in range(len(vecs[0])):
        if vecs[0][i] != vecs[1][i]:
            dist = dist + 1

    #Return the Hamming distance
    return dist

#Finds the nearest code word in a code given some vector 
def find_nearest_code_word(vec, code):
    #Instantiate the distance to infinity since we want to minimize it
    dist = numpy.inf

    #Also we are looking for a code word so we track the index
    index = 0

    #Loop through all code words (This is a brute force search)
    for i in range(len(code)):
        #Calculate the hamming distance
        vec_dist = hamming_distance(vec, code[i])

        #Check if the distance is smaller at the ith iteration
        if vec_dist < dist:
            dist = vec_dist
            index = i

    #Return the code word at the index of the minimum distance code
    #word relative to the one passed in
    return code[index]


#This function extracts the first n bits from a code word (presumably the information bits)
def get_information_bits(vec, n):
    #Instantiate the information bit list
    information_bits = []

    #Loop through the first n bits
    for i in range(n):
        #Append the first n bits (they are info bits)
        information_bits.append(vec[i])

    #Return the list of information bits
    return information_bits

#Generate all code words for all codes and save to memory
print("Generating the binary Golay code...", flush=True)
BINARY_GOLAY_CODE = generate_all_code_words(BINARY_GOLAY_GENERATOR_MATRIX, 2)
print("Generating the extended binary Golay code...", flush=True)
EXTENDED_BINARY_GOLAY_CODE = generate_all_code_words(EXTENDED_BINARY_GOLAY_GENERATOR_MATRIX, 2)

#TODO: Generate all code words for the ternary Golay codes

#TODO: Look into Golay polynomial and BCH decoding

#Initialize the Flask application
server = Flask(__name__)

#Apply CORS middleware to server
CORS(server)

#This function encodes a list of code words according to the binary golay code generator matrix
@cross_origin()
@server.route("/binary/encode", methods=['POST'])
def binary_golay_encode():
    try:
        information_bits = request.get_json(force=True).informationBits
        code_words = []
        for vector in information_bits:
            code_word = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(len(vector)):
                if vector[i] == 1:
                    code_word = vector_addition(BINARY_GOLAY_GENERATOR_MATRIX[i], code_word, 2)
            code_words.append(code_word)
        return { "codeWords" : code_words }
    except Exception as e:
        return { "message" : str(e) }

#This function decodes a list of vectors according to the binary golay code
@cross_origin()
@server.route("/binary/decode")
def binary_golay_decode():
    try:
        code_words = request.get_json(force=True).codeWords
        information_bits = []
        for word in code_words:
            information_bits.append(get_information_bits(find_nearest_code_word(word, BINARY_GOLAY_CODE), 12))
        return { "informationBits" : information_bits }
    except Exception as e:
        return { "message" : str(e) }

#This function encodes a list of code words according to the extended binary golay code generator matrix
@cross_origin()
@server.route("/extended-binary/encode", methods=['POST'])
def extended_binary_golay_encode():
    try:
        information_bits = request.get_json(force=True).get('informationBits')
        code_words = []
        for vector in information_bits:
            code_word = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(len(vector)):
                if vector[i] == 1:
                    code_word = vector_addition(EXTENDED_BINARY_GOLAY_GENERATOR_MATRIX[i], code_word, 2)
            code_words.append(code_word)
        return { "codeWords" : code_words }
    except Exception as e:
        return { "message" : str(e) }

#This function decodes a list of vectors according to the extended binary golay code
@cross_origin()
@server.route("/extended-binary/decode", methods=['POST'])
def extended_binary_golay_decode():
    try:
        code_words = request.get_json(force=True).get('codeWords')
        information_bits = []
        for word in code_words:
            information_bits.append(get_information_bits(find_nearest_code_word(word, EXTENDED_BINARY_GOLAY_CODE), 12))
        return { "informationBits" : information_bits }
    except Exception as e:
        return { "message" : str(e) }

#This function transmits a binary code word according to some stochastic error probability
@cross_origin()
@server.route("/binary-channel/transmit", methods=['POST'])
def binary_channel_transmit():
    try:
        body = request.get_json(force=True)
        code_words = body.codeWords
        error_rate = body.errorRate
        noisy_code_words = []
        for word in code_words:
            noisy_word = []
            for bit in word:
                rng = numpy.random.binomial(1, error_rate, 1)
                if rng == 1:
                    noisy_word.append((bit + 1) % 2)
                else:
                    noisy_word.append(bit)
            noisy_code_words.append(noisy_word)
        return { "noisyCodeWords" : noisy_code_words }
    except Exception as e:
        return { "message" : str(e) }

#TODO: Write the ternary golay encoding function
@server.route("/ternary/encode")
def ternary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the ternary golay decoding function
@server.route("/ternary/decode")
def ternary_golay_decode():
    return { "message" : "Hello, World!" }

#TODO: Write the extended ternary golay encoding function
@server.route("/extended-ternary/encode")
def extended_ternary_golay_encode():
    return { "message" : "Hello, World!" }

#TODO: Write the extended ternary golay decoding function
@server.route("/extended-ternary/decode")
def extended_ternary_golay_decode():
    return { "message" : "Hello, World!" }

#TODO: Write the ternary channel transmission function
@server.route("/ternary-channel/transmit")
def ternary_channel_transmit():
    return { "message" : "Hello, World!" }