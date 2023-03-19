
components = [
    # component1,
    # component2
]
# one of these per line of the CIRCUIT block
component_dict = {
    # Node IDs
    "N1":None, # in
    "N2":None, # out

    # Component value (only one)
    #"L":None, # inductance
    #"C":None, # capacitance
    #"R":None, # resistance
    #"G":None, # conductance
}

# read all lines in TERMS into one dict, since there is only one input
terms_dict = {
    # Source type & value
    #"VT":None, # Thevenin Voltage
    #"IN":None, # Norton Current

    # Source resistance or conductance
    #"RS":None,
    #"GS":None,

    # Load resistance
    "RL":None, # load

    # Frequency sweep settings
    "Fstart":None,
    "Fend":None,

}
# read from all of OUTPUT, with \n as delimiter and " " as :
output_dict = {
    #"param":"unit"

    # examples:
    "Vin":"V",
    "Vout":"V",
    "Iin":"A",
    "Iout":"A",
    "Pin":"W",
    "Zout":"Ohms",
    "Av":None, # MUST accept lines without a unit!
    "Ai":None,
}

# universal line to dict converter (perform error checking on output later!)
# this avoids repeating the code for reading the file
def read_block(lines,pair_splitter,delimiter):
    # create empty dict
    # split by delimiter (e.g. " " or "\n")
    # for element
        # split by key_value_separator (e.g. "=" or " ")
        # check no. elements ==2
        # 0 is key, 1 is value
    block_dicts=[]
    for line in lines:
        line_dict={}
        for element in line.split(delimiter):
            # print(element,end = ' -> ')
            pair=element.split(pair_splitter)
            # print(pair,end = ' -> ')
            if len(pair)==2:
                key,value=pair
                line_dict[key]=value
                # print(f"\"{key}\":\"{value}\"")
            elif len(pair)==1:
                key=pair[0]
                line_dict[key]=None
                # print(f"\"{key}\":\"{None}\"")
            else:
                print("Failed to split")
        block_dicts.append(line_dict)
    return block_dicts

# def read_output_block(lines):
#     #for line
#         # split by spaces
#         # check no. elements <=2
#         # add to dict 
#             # 0 is key, 1 is value (if no value, None)

# def read_terms_block(lines):
#     # for line
#         # split by spaces
#         # for element
#             # split by =
#             # check no. elements==2
#             # add to dict
#                 # 0 is key, 1 is value

# def read_circuit_block(lines):
#     # create empty dict to store all components
#     # for line
#         # split by spaces
#         # check no. elements ==3
#         # create empty component dict inside master dict
#         # for element
#             # split by =
#             # check no. elements ==2
#             # add to component dict
#                 # 0 is key, 1 is value


def extract_block(net,name):
    startTag=f"<{name}>"
    endTag=f"</{name}>"

    idxStart=None
    idxEnd=None

    for idx,line in enumerate(net):
        if startTag in line:
            if idxStart is None:
                idxStart=idx+1
            else:
                print(f"Net error: Multiple {startTag} tags")
        elif endTag in line:
            if idxEnd is None:
                idxEnd=idx
            else:
                print(f"Net error: Multiple {endTag} tags")
    if not (idxStart is None or idxEnd is None):
        if idxStart<idxEnd:
            block=net[idxStart:idxEnd]
            # print(f"\nExtracted block {name}:")
            # print(block)
            return block
        else:
            print(f"Net error: {endTag} before {startTag}")
    else:
        print(f"Net error: could not find either {startTag} or {endTag}")


def read_net(filename):
    # open file
    # remove comments
    # remove empty lines
    # locate blocks
        # ensure block has end
        # ensure only one of each
        # ensure each block is defined
    # convert blocks to dicts using functions
    # output these dicts

    file=open(filename,"r")
    rawlines=file.readlines()
    file.close()
    lines=[]
    for line in rawlines:
        # remove leading and trailing whitespace 
        line=line.strip()
        # only add if line isn't empty or a comment
        if not (len(line.strip())==0 or line[0] == "#"):
            lines.append(line)

    # print(lines)
    circuit=extract_block(lines,"CIRCUIT")
    terms=extract_block(lines,"TERMS")
    output=extract_block(lines,"OUTPUT")

    print("Extracting key:value pairs for CIRCUIT")
    circuit_dicts=read_block(circuit,"="," ")
    print("Extracting key:value pairs for TERMS")
    for line_dict in read_block(terms,"="," "):
        terms_dict.update(line_dict)
    print("Extracting key:value pairs for OUTPUT")
    for line_dict in read_block(output," ","\n"):
        output_dict.update(line_dict)
    
    print(f"Components: {circuit_dicts}")
    print(f"Terms: {terms_dict}")
    print(f"Output: {output_dict}")

    return circuit_dicts,terms_dict,output_dict



    
    

    

read_net("./nets/a_Test_Circuit_1.net")