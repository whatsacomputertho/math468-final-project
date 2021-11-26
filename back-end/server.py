#Import dependencies
from flask import Flask, request
from flask_cors import CORS, cross_origin
import numpy, json

#Print the fact that the script is being run
print("Server initializing...", flush=True)

#Initialize the Flask application
server = Flask(__name__)

#Apply CORS middleware to server
CORS(server)

#This function generates a list of all code words by linearly combining all elements of the
#generator matrix
def generate_all_code_words(generator_matrix):
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
                #Linearly combine an element of the generator matrix with a code word
                code_word = numpy.bitwise_xor(generator_matrix[i], code_words[j])
                
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

#Extended binary golay code generator matrix
BINARY_EXTENDED_GOLAY_MATRIX = [numpy.uint32(8391153), numpy.uint32(4195578), numpy.uint32(2097789), numpy.uint32(1050942), numpy.uint32(527517), numpy.uint32(265806),
                                numpy.uint32(134949),  numpy.uint32(69522), numpy.uint32(34761), numpy.uint32(17382), numpy.uint32(9559), numpy.uint32(6827)]

#Prompt the user that the binary extended golay code is being generated
print("Generating the binary extended golay code...")

#Extended binary golay code generated from the generator matrix
BINARY_EXTENDED_GOLAY_CODE = generate_all_code_words(BINARY_EXTENDED_GOLAY_MATRIX)

#Read the decoder lut into memory
print("Reading decoder lookup table...")

#Load the in-memory luts mapping code words to themselves, and noise to code words
f = open('./luts/golay-code-lut.json', 'r')
binary_extended_golay_code_lut = json.load(f).get('lut')
f.close()
f = open('./luts/golay-noise-lut.json', 'r')
binary_extended_noise_lut = json.load(f).get('lut')
f.close()

#Returns the unpacked bits of the pixel's rgb values
def get_pixel_bits(image_data, i):
    r = numpy.uint8(image_data[4*i])
    g = numpy.uint8(image_data[(4*i) + 1])
    b = numpy.uint8(image_data[(4*i) + 2])
    return [r, g, b]

#Returns the hamming distance between a pixel and a code word of the Golay code
def hamming_distance(pixel, code_word):
    r = numpy.unpackbits(numpy.uint8(pixel[0]))
    g = numpy.unpackbits(numpy.uint8(pixel[1]))
    b = numpy.unpackbits(numpy.uint8(pixel[2]))
    code_word_r_bits = numpy.unpackbits(numpy.uint8(numpy.right_shift(numpy.bitwise_and(code_word, numpy.uint32(16711680)), 16)))
    code_word_g_bits = numpy.unpackbits(numpy.uint8(numpy.right_shift(numpy.bitwise_and(code_word, numpy.uint32(65280)), 8)))
    code_word_b_bits = numpy.unpackbits(numpy.uint8(numpy.bitwise_and(code_word, numpy.uint32(255))))
    distance = 0
    for i in range(8):
        if(r[i] != code_word_r_bits[i]):
            distance = distance + 1
        if(g[i] != code_word_g_bits[i]):
            distance = distance + 1
        if(b[i] != code_word_b_bits[i]):
            distance = distance + 1
    return distance

#Returns either the corresponding code word to the pixel value, or returns nothing
def check_lut_for_pixel(pixel):
    pixel_value = numpy.bitwise_xor(numpy.left_shift(numpy.uint32(pixel[0]), 16), numpy.left_shift(numpy.uint32(pixel[1]), 8))
    pixel_value = str(numpy.bitwise_xor(pixel_value, numpy.uint32(pixel[2])))
    global binary_extended_golay_code_lut
    if pixel_value in binary_extended_golay_code_lut.keys():
        code_word = binary_extended_golay_code_lut.get(pixel_value)
        return code_word
    global binary_extended_noise_lut
    if pixel_value in binary_extended_noise_lut.keys():
        code_word = binary_extended_noise_lut.get(pixel_value)
        return code_word
    else:
        return None

#Writes a pixel/code word pair to the lut for future reference
def write_pixel_decoding_to_lut(pixel, code_word):
    try:
        pixel_value = numpy.bitwise_xor(numpy.left_shift(numpy.uint32(pixel[0]), 16), numpy.left_shift(numpy.uint32(pixel[1]), 8))
        pixel_value = str(numpy.bitwise_xor(pixel_value, numpy.uint32(pixel[2])))
        global binary_extended_noise_lut
        binary_extended_noise_lut[pixel_value] = int(code_word)
        keys = list(binary_extended_noise_lut.keys())
        if(len(keys) > 5000):
            del binary_extended_noise_lut[keys[0]]
        f = open('./luts/golay-noise-lut.json', 'w')
        f.write(json.dumps({'lut':binary_extended_noise_lut}))
        f.close()
        return True
    except Exception as e:
        print(e)
        return False

#Returns the minimum distance code word given a pixel and the Golay code (i.e. it decodes the code word)
#First, the function checks for a kvp in the lut with the key value "pixel"
#If found, it is returned, otherwise, the pixel is decoded and written to the lut
def minimum_distance_code_word(pixel, code):
    md_code_word = check_lut_for_pixel(pixel)
    if md_code_word is None:
        md_code_word = numpy.uint32(0)
        minimum_distance = numpy.inf
        for code_word in code:
            distance = hamming_distance(pixel, code_word)
            if distance < minimum_distance:
                minimum_distance = distance
                md_code_word = code_word
        write_pixel_decoding_to_lut(pixel, md_code_word)
    return md_code_word

#For the individual code-word interface, this is used to convert the list which is sent to the back end
#to a "pixel" for decoding
def bit_list_to_pixel(bit_list):
    r = 0
    g = 0
    b = 0
    for i in range(len(bit_list)):
        if bit_list[i] == 1:
            if i < 8:
                r = r + (2**(8-(i+1)))
            elif i >= 8 and i < 16:
                g = g + (2**(16-(i+1)))
            else:
                b = b + (2**(24-(i+1)))
    r = numpy.uint8(r)
    g = numpy.uint8(g)
    b = numpy.uint8(b)
    return [r, g, b]

#For the individual code-word interface, this is used to convert the code word back into a list of decoded
#bits for display
def decoded_code_word_to_bit_list(code_word):
    info_bits = numpy.right_shift(numpy.bitwise_and(code_word, numpy.uint32(16773120)), 12)
    info_bits_1 = numpy.unpackbits(numpy.uint8(numpy.right_shift(numpy.bitwise_and(info_bits, numpy.uint32(3840)), 8)))
    info_bits_2 = numpy.unpackbits(numpy.uint8(numpy.bitwise_and(info_bits, numpy.uint32(255))))
    bit_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(8):
        if i < 4:
            if info_bits_2[i] == 1:
                bit_list[i + 4] = 1
        else:
            if info_bits_2[i] == 1:
                bit_list[i + 4] = 1
            if info_bits_1[i] == 1:
                bit_list[i - 4] = 1
    return bit_list

#Returns the original pixel given two decoded code words
def get_pixel_from_code_words(code_word_1, code_word_2):
    info_bits_1 = numpy.bitwise_and(code_word_1, numpy.uint32(16773120))
    info_bits_2 = numpy.right_shift(numpy.bitwise_and(code_word_2, numpy.uint32(16773120)), 12)
    pixel_data = numpy.bitwise_xor(info_bits_1, info_bits_2)
    r = numpy.uint8(numpy.right_shift(numpy.bitwise_and(pixel_data, numpy.uint32(16711680)), 16))
    g = numpy.uint8(numpy.right_shift(numpy.bitwise_and(pixel_data, numpy.uint32(65280)), 8))
    b = numpy.uint8(numpy.bitwise_and(pixel_data, numpy.uint32(255)))
    return [r, g, b]

#Flips the pixel bits according to the given error probability
def transmit_pixel(pixel_data, error_rate):
    pixel_data_clone = [numpy.unpackbits(pixel_data[0]), numpy.unpackbits(pixel_data[1]), numpy.unpackbits(pixel_data[2])]
    for i in range(len(pixel_data_clone)):
        for j in range(len(pixel_data_clone[i])):
            rng = numpy.random.binomial(1, error_rate, 1)
            if(rng == 1):
                if(pixel_data_clone[i][j] == 0):
                    pixel_data_clone[i][j] = 1
                else:
                    pixel_data_clone[i][j] = 0
    r = numpy.packbits(pixel_data_clone[0])[0]
    g = numpy.packbits(pixel_data_clone[1])[0]
    b = numpy.packbits(pixel_data_clone[2])[0]
    return [r, g, b]

#Encodes a pixel according to the binary extended golay matrix
def encode_pixel(pixel_data):
    pixel_data_clone = [numpy.unpackbits(pixel_data[0]), numpy.unpackbits(pixel_data[1]), numpy.unpackbits(pixel_data[2])]
    codeword_1 = numpy.uint32(0)
    codeword_2 = numpy.uint32(0)
    for i in range(len(pixel_data_clone)):
        for j in range(len(pixel_data_clone[i])):
            if(pixel_data_clone[i][j] == numpy.uint8(1)):
                if(i == 0):
                    codeword_1 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j], codeword_1)
                elif(i == 1 and j < 4):
                    codeword_1 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[8 + j], codeword_1)
                elif(i == 1 and j >= 4):
                    codeword_2 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j - 4], codeword_2)
                elif(i == 2):
                    codeword_2 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j + 4], codeword_2)
    return [codeword_1, codeword_2]

#For the single code-word interface, used to encode the information bits specified by the user
def encode_info_bit_list(bit_list):
    code_word = numpy.uint32(0)
    for i in range(len(bit_list)):
        if bit_list[i] == 1:
            code_word = numpy.bitwise_xor(code_word, BINARY_EXTENDED_GOLAY_MATRIX[i])
    return code_word

#For the single code-word interface, used to convert the encoded information to a list of bits
def encoded_code_word_to_bit_list(code_word):
    bit_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    r = numpy.unpackbits(numpy.uint8(numpy.right_shift(numpy.bitwise_and(code_word, numpy.uint32(16711680)), 16)))
    g = numpy.unpackbits(numpy.uint8(numpy.right_shift(numpy.bitwise_and(code_word, numpy.uint32(65280)), 8)))
    b = numpy.unpackbits(numpy.uint8(numpy.bitwise_and(code_word, numpy.uint32(255))))
    for i in range(8):
        if r[i] == 1:
            bit_list[i] = 1
        if g[i] == 1:
            bit_list[i+8] = 1
        if b[i] == 1:
            bit_list[i+16] = 1
    return bit_list

#Converts the encoded pixels two rgb pixels for visualization
def get_encoded_pixels(code_words):
    r1_bits = numpy.right_shift(numpy.bitwise_and(code_words[0], numpy.uint32(16711680)), 16)
    g1_bits = numpy.right_shift(numpy.bitwise_and(code_words[0], numpy.uint32(65280)), 8)
    b1_bits = numpy.bitwise_and(code_words[0], 255)
    r2_bits = numpy.right_shift(numpy.bitwise_and(code_words[1], numpy.uint32(16711680)), 16)
    g2_bits = numpy.right_shift(numpy.bitwise_and(code_words[1], numpy.uint32(65280)), 8)
    b2_bits = numpy.bitwise_and(code_words[1], 255)
    r1 = numpy.uint8(r1_bits)
    g1 = numpy.uint8(g1_bits)
    b1 = numpy.uint8(b1_bits)
    r2 = numpy.uint8(r2_bits)
    g2 = numpy.uint8(g2_bits)
    b2 = numpy.uint8(b2_bits)
    return [[r1, g1, b1], [r2, g2, b2]]

#Converts the parity check bits of the encoded pixel into a pixel itself for visualization
def get_parity_check_pixel(code_words):
    parity_bits_1 = numpy.bitwise_and(numpy.uint32(4095), code_words[0])
    parity_bits_2 = numpy.bitwise_and(numpy.uint32(4095), code_words[1])
    r_bits = numpy.right_shift(numpy.bitwise_and(parity_bits_1, numpy.uint32(4080)), 4)
    g_bits_2 = numpy.bitwise_and(parity_bits_1, numpy.uint32(15))
    g_bits_1 = numpy.right_shift(numpy.bitwise_and(parity_bits_2, numpy.uint32(3840)), 4)
    b_bits = numpy.bitwise_and(parity_bits_2, numpy.uint32(255))
    r = numpy.uint8(r_bits)
    g = numpy.uint8(numpy.bitwise_xor(g_bits_1, g_bits_2))
    b = numpy.uint8(b_bits)
    return [r, g, b]

#Encodes all image data
def encode_image(image_data, width, height, is_parity_check_image):
    encoded_image_data = []
    if(is_parity_check_image):
        for i in range(height):
            for j in range(width):
                pixel_bits = get_pixel_bits(image_data, j+(i*width))
                encoded_image_data.append(int(pixel_bits[0]))
                encoded_image_data.append(int(pixel_bits[1]))
                encoded_image_data.append(int(pixel_bits[2]))
                encoded_image_data.append(255)
            for j in range(width):
                parity_pixel_bits = get_parity_check_pixel(encode_pixel(get_pixel_bits(image_data, j+(i*width))))
                encoded_image_data.append(int(parity_pixel_bits[0]))
                encoded_image_data.append(int(parity_pixel_bits[1]))
                encoded_image_data.append(int(parity_pixel_bits[2]))
                encoded_image_data.append(255)
    else:
        for i in range(int(len(image_data)/4)):
            pixels = get_encoded_pixels(encode_pixel(get_pixel_bits(image_data, i)))
            encoded_image_data.append(int(pixels[0][0]))
            encoded_image_data.append(int(pixels[0][1]))
            encoded_image_data.append(int(pixels[0][2]))            
            encoded_image_data.append(255)
            encoded_image_data.append(int(pixels[1][0]))
            encoded_image_data.append(int(pixels[1][1]))
            encoded_image_data.append(int(pixels[1][2]))
            encoded_image_data.append(255)
    return encoded_image_data

#Transmits image data according to a given stochastic error probability
def transmit_image(image_data, error_rate):
    noisy_image_data = []
    for i in range(int(len(image_data)/4)):
        pixel = transmit_pixel(get_pixel_bits(image_data, i), error_rate)
        noisy_image_data.append(int(pixel[0]))
        noisy_image_data.append(int(pixel[1]))
        noisy_image_data.append(int(pixel[2]))
        noisy_image_data.append(255)
    return noisy_image_data

#Decodes the noisy image data
def decode_image(image_data):
    decoded_image_data = []
    for i in range(int(len(image_data)/8)):
        index = i*2
        code_word_1 = minimum_distance_code_word(get_pixel_bits(image_data, index), BINARY_EXTENDED_GOLAY_CODE)
        code_word_2 = minimum_distance_code_word(get_pixel_bits(image_data, index + 1), BINARY_EXTENDED_GOLAY_CODE)
        pixel = get_pixel_from_code_words(code_word_1, code_word_2)
        decoded_image_data.append(int(pixel[0]))
        decoded_image_data.append(int(pixel[1]))
        decoded_image_data.append(int(pixel[2]))
        decoded_image_data.append(255)
    return decoded_image_data

#For single code-word interface, this decodes the message with errors
def decode_message(bit_list, code):
    code_word = minimum_distance_code_word(bit_list_to_pixel(bit_list), code)
    info_bits = decoded_code_word_to_bit_list(code_word)
    return info_bits

#This function encodes a list of code words according to the extended binary golay code generator matrix
@cross_origin()
@server.route("/extended-binary/encode", methods=['POST'])
def extended_binary_golay_encode():
    data = request.get_json()
    information_bits = data.get("informationBits")
    code_word = encoded_code_word_to_bit_list(encode_info_bit_list(information_bits))
    return { "codeWord" : code_word }

#This function decodes a list of vectors according to the extended binary golay code
@cross_origin()
@server.route("/extended-binary/decode", methods=['POST'])
def extended_binary_golay_decode():
    data = request.get_json()
    message = data.get("message")
    decoded_message = decode_message(message, BINARY_EXTENDED_GOLAY_CODE)
    return { "informationBits" : decoded_message }

#This function encodes a list of code words according to the extended binary golay code generator matrix
@cross_origin()
@server.route("/extended-binary/encode-image", methods=['POST'])
def extended_binary_golay_encode_image():
    data = request.get_json()
    image_data = list(data.get("informationBits").values())
    width = data.get("width")
    height = data.get("height")
    encoded_image = encode_image(image_data, width, height, False)
    return { "width" : width * 2, "height" : height, "data" : encoded_image }

#This function transmits a binary code word according to some stochastic error probability
@cross_origin()
@server.route("/binary-channel/transmit-image", methods=['POST'])
def binary_channel_transmit():
    data = request.get_json()
    image_data = list(data.get("encodedImage").values())
    width = data.get("width")
    height = data.get("height")
    error_rate = float(data.get("errorRate"))
    if(error_rate != 0):
        noisy_image = transmit_image(image_data, error_rate)
    else:
        noisy_image = image_data
    return { "width" : width, "height" : height, "data" : noisy_image }

#This function decodes a list of vectors according to the extended binary golay code
@cross_origin()
@server.route("/extended-binary/decode-image", methods=['POST'])
def extended_binary_golay_decode_image():
    data = request.get_json()
    image_data = list(data.get("noisyImage").values())
    width = data.get("width")
    height = data.get("height")
    decoded_image = decode_image(image_data)
    return { "width" : int(width / 2), "height" : height, "data" : decoded_image }