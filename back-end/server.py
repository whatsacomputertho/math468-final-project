#Import dependencies
from flask import Flask, request
from flask_cors import CORS, cross_origin
import numpy

#Print the fact that the script is being run
print("Server initializing...", flush=True)

#Initialize the Flask application
server = Flask(__name__)

#Apply CORS middleware to server
CORS(server)

#TODO: Binary golay code generator matrix
BINARY_EXTENDED_GOLAY_MATRIX = [numpy.uint32(8391153), numpy.uint32(4195578), numpy.uint32(2097789), numpy.uint32(1050942), numpy.uint32(527517), numpy.uint32(265806),
                                numpy.uint32(134949),  numpy.uint32(69522), numpy.uint32(34761), numpy.uint32(17382), numpy.uint32(9559), numpy.uint32(6827)]

#Returns the unpacked bits of the pixel's rgb values
def get_pixel_bits(image_data, i):
    r = numpy.uint8(image_data[4*i])
    g = numpy.uint8(image_data[(4*i) + 1])
    b = numpy.uint8(image_data[(4*i) + 2])
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
                if(i == 1):
                    codeword_1 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j], codeword_1)
                elif(i == 2 and j < 4):
                    codeword_1 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[8 + j], codeword_1)
                elif(i == 2 and j >= 4):
                    codeword_2 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j - 4], codeword_2)
                elif(i == 3):
                    codeword_2 = numpy.bitwise_xor(BINARY_EXTENDED_GOLAY_MATRIX[j + 4], codeword_2)
    return [codeword_1, codeword_2]

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

#This function encodes a list of code words according to the binary golay code generator matrix
@cross_origin()
@server.route("/binary/encode", methods=['POST'])
def binary_golay_encode():
    return { "message" : "Hello, World!" }

#This function decodes a list of vectors according to the binary golay code
@cross_origin()
@server.route("/binary/decode")
def binary_golay_decode():
    return { "message" : "Hello, World!" }

#This function encodes a list of code words according to the extended binary golay code generator matrix
@cross_origin()
@server.route("/extended-binary/encode", methods=['POST'])
def extended_binary_golay_encode():
    return { "message" : "Hello, World!" }

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

#This function decodes a list of vectors according to the extended binary golay code
@cross_origin()
@server.route("/extended-binary/decode", methods=['POST'])
def extended_binary_golay_decode():
    return { "message" : "Hello, World!" }

#This function transmits a binary code word according to some stochastic error probability
@cross_origin()
@server.route("/binary-channel/transmit-image", methods=['POST'])
def binary_channel_transmit():
    data = request.get_json()
    image_data = list(data.get("encodedImage").values())
    width = data.get("width")
    height = data.get("height")
    error_rate = float(data.get("errorRate"))
    noisy_image = transmit_image(image_data, error_rate)
    print("running")
    return { "width" : width, "height" : height, "data" : noisy_image }

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