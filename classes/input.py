
import sys
import ast


valid_args={
    "-i":str,
    "-j":int,
    "-d":list,
    "-p":list
}


def parse_arguments():
    raw_args=sys.argv[1:]
    args={}
    for idx,string in enumerate(raw_args):
        # Check if an argument or value
        if string[0]=="-":
            # Check if a valid argument
            if string in valid_args:
                # Attempt to convert type
                value=raw_args[idx+1]
                # print(value)
                value=value.replace("[","").replace("]","")
                try:
                    if valid_args[string]==list:
                        args[string]=value.split(",")
                    else:
                        args[string]=valid_args[string](value)
                except:
                    print(f"Argument {string} has invalid value \"{value}\", should be type {valid_args[string]}")
                    sys.exit()
            else:
                # Unknown argument
                print(f"Unknown argument {string}")
                sys.exit()
    # print(f"Arguments: {args}")
    if not "-i"  in args:
        print("Missing argument \"-i\"")
        sys.exit()
    return args
            






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


def parse_net(path):
    # open file
    # remove comments
    # remove empty lines
    # locate blocks
        # ensure block has end
        # ensure only one of each
        # ensure each block is defined
    # convert blocks to dicts using functions
    # output these dicts
    try:
        file=open(path+".net","r")
    except:
        print(f"Could not find {path}.net")
        sys.exit()
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

    terms_dict={}
    circuit_dicts=[]
    output_dict={}

    print("Extracting key:value pairs for CIRCUIT")
    circuit_dicts=read_block(circuit,"="," ")
    print("Extracting key:value pairs for TERMS")
    for line_dict in read_block(terms,"="," "):
        terms_dict.update(line_dict)
    print("Extracting key:value pairs for OUTPUT")
    for line_dict in read_block(output," ","\n"):
        output_dict.update(line_dict)
    
    # print(f"Components: {circuit_dicts}")
    # print(f"Terms: {terms_dict}")
    # print(f"Output: {output_dict}")

    return circuit_dicts,terms_dict,output_dict

