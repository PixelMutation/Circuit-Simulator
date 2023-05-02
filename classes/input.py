
import sys
import ast
import re


valid_args={
    "-i":str, # input
    "-o":str, # output
    # "-l":str, # log
    # "-j":int, # multiprocessing
    "-d":list,# display plot
    "-p":list # generate plot
}

# read and check command line arguments
def parse_arguments():
    raw_args=sys.argv[1:] # first arg is python filename so remove
    args={}
    # Help statement
    if len(raw_args)==0 or raw_args[0]=="-h":
        msg=[
            "Cascade Circuit Simuator",
            "Usage:",
            "   python analyse_circuit.py input_path output_path optional_args",
            "   python analyse_circuit.py input_path optional_args",
            "   python analyse_circuit.py optional_args",
            "Optional Arguments:",
            "   -i input_path       e.g. nets/b_CR.net  Sets input path (suffix not required)",
            "   -o output_path      e.g. out/b_CR.csv   Sets the output path, uses input path if not set",
            "   -p columns_list     e.g. [2,3,4]        Plots the listed columns from the CSV, saves PNG to output path",
            "   -d                                      Displays the plots in an interactive window"
        ]
        print("\n".join(msg))
        sys.exit()
    # First check for paths given without -i or -o
    processed=0
    # if 1st arg has no "-", it must be the input path
    if raw_args[0][0]!="-":
        args["-i"]=raw_args[0]
        processed=1
        # if 2nd arg also has no "-", it must be the output path
        if len(raw_args)>1 and raw_args[1][0]!="-":
            args["-o"]=raw_args[1]
            processed=2
            # if 3rd arg also has no "-", it must be the log path
            # if len(raw_args)>2 and raw_args[2][0]!="-":
            #     args["-l"]=raw_args[2]
            #     processed=3
    
    # Now handle the remaining arguments
    if len(raw_args)>=processed:
        for i,string in enumerate(raw_args[processed:]):
            idx=i+processed
            # Check if an argument or value
            if string[0]=="-":
                # Check if a valid argument
                if string in valid_args:
                    # Get value of argument
                    if len(raw_args)>idx+1:
                        value=raw_args[idx+1]
                    elif string != "-d":
                        raise AttributeError(f"Argument {string} has no corresponding value")
                    else:
                        value=""
                    # print(value)
                    value=value.replace("[","").replace("]","")
                    # Attempt to convert type
                    try:
                        if valid_args[string]==list:
                            args[string]=value.split(",")
                        else:
                            args[string]=valid_args[string](value)
                    except:
                        raise TypeError(f"Argument {string} has invalid value \"{value}\", should be type {valid_args[string]}")
                else:
                    # Unknown argument
                    raise Exception(f"Unknown argument {string}")
    

    if not "-i" in args:
        raise Exception(f"Missing input argument (\"-i\" or pos 0)")
    # If output or log paths not provided, use input path
    if not "-o" in args:
        args["-o"]=args["-i"]
    # if not "-l" in args:
    #     args["-l"]=args["-i"]
    # remove path suffixes from args
    for arg in ["-i","-o"]:
        args[arg]=args[arg].replace(".net","")
        args[arg]=args[arg].replace(".csv","")
        # args[arg]=args[arg].replace(".log","")
    print(f"Arguments: {args}")
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
        # if delimiter next to pair splitter, remove it (e.g. n1 =5 -> n1=5)
        line=line.replace(pair_splitter+delimiter,pair_splitter)
        line=line.replace(delimiter+pair_splitter,pair_splitter)
        for element in line.split(delimiter):
            # print(element,end = ' -> ')
            pair=element.split(pair_splitter)
            # print(pair,end = ' -> ')
            val=None
            if len(pair)==2:
                key,value=pair
                val=value
                # print(f"\"{key}\":\"{value}\"")
            elif len(pair)==1:
                key=pair[0]
                val=None
                # print(f"\"{key}\":\"{None}\"")
            else:
                raise Exception(f"Failed to split \"{element}\" into a key:value pair")
            
        block_dicts.append(line_dict)
    return block_dicts

# Split net file into blocks using the start/end tags
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
                raise SyntaxError(f"Net: Multiple {startTag} tags")
        elif endTag in line:
            if idxEnd is None:
                idxEnd=idx
            else:
                raise SyntaxError(f"Net: Multiple {endTag} tags")
    if not (idxStart is None or idxEnd is None):
        if idxStart<idxEnd:
            block=net[idxStart:idxEnd]
            # print(f"\nExtracted block {name}:")
            # print(block)
            return block
        else:
            raise SyntaxError(f"Net: {endTag} before {startTag}")
    else:
        raise SyntaxError(f"Net: could not find either {startTag} or {endTag}")

class Net:
    terms_dict=None
    circuit_dicts=None
    output_dicts=None

# main function to convert the net into dictionaries
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
        raise FileNotFoundError(f"Could not find {path}.net")
        sys.exit()
    rawlines=file.readlines()
    file.close()
    lines=[]
    for line in rawlines:
        # remove leading and trailing whitespace 
        line=line.strip()
        # remove consecutive whitespace
        line=re.sub('\s{2,}', ' ', line)
        # only add if line isn't empty or a comment
        if not (len(line.strip())==0 or line[0] == "#"):
            lines.append(line)

    # print(lines)
    circuit=extract_block(lines,"CIRCUIT")
    terms=extract_block(lines,"TERMS")
    output=extract_block(lines,"OUTPUT")

    terms_dict={}
    circuit_dicts=[]

    print("Extracting key:value pairs for CIRCUIT")
    circuit_dicts=read_block(circuit,"="," ")
    # print(f"Components: {circuit_dicts}")

    print("Extracting key:value pairs for TERMS")
    for line_dict in read_block(terms,"="," "):
        terms_dict.update(line_dict)
    # print(f"Terms: {terms_dict}")

    print("Extracting key:value pairs for OUTPUT")
    # replace first space with colon and remove further spaces
    # this allows spaces betwween prefixes, dB and unit
    for idx,line in enumerate(output): 
        line=line.replace(" ",":",1)
        line=line.replace(" ","")
        output[idx]=line

    # each line is a new (possible duplicate) variable
    output_dicts=read_block(output,":"," ")

    net = Net()
    net.circuit_dicts=circuit_dicts
    net.output_dicts=output_dicts
    net.terms_dict=terms_dict
    
    return net
