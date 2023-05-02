import time
import os
import matplotlib.pyplot as plt

from classes.input import parse_net,parse_arguments
from classes.circuit import Circuit
from classes.output import Output
from classes.terms import Terms

start_process=time.process_time_ns()

args=parse_arguments()

# function to print stack trace during exception (from https://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python)
def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

# Utility function for printing and timing each section of the program
start_section=None
def startSection(name):
    global start_section
    # Print duration of previous section (if not currently in first section)
    if not start_section is None:
        print(f"# Section took {((time.process_time_ns()-start_section)/(10**9)):.3f}s ")
    print(name.center(70,"-"))
    start_section=time.process_time_ns()

try:
    startSection("Reading Net File")
    net=parse_net(args["-i"])

    startSection("Creating Terms object")
    terms=Terms(net.terms_dict)
    print(terms)

    startSection("Creating Circuit object")
    circuit=Circuit(net.circuit_dicts,terms)
    # print(circuit)
    print(circuit.get_ascii_art())

    startSection("Creating Output Object ")
    output=Output(net.output_dicts,circuit,terms)
    print(output)

    startSection("Calculating component ABCD matrices")
    circuit.calc_component_ABCDs()

    startSection("Calculating cascade ABCD matrices")
    circuit.calc_overall_ABCDs()
    print(circuit)

    startSection("Calculating variables")
    output.calc_variables() # Requests each var to be calculated by circuit class

    startSection("Formatting output variables")
    output.convert_variables() # Converts each value to chosen units and stores inside Column object

    startSection("Saving output as CSV")
    output.save_csv(args["-o"]) # Convert column objects to CSV

    if "-p" in args:
        startSection("Generating plots against frequency")
        output.plot(args["-p"],args["-o"],"-d" in args)

    startSection("END")
    print(f"Program took {((time.process_time_ns()-start_process)/(10**9)):.2f}s (process time)")
    if "-d" in args and "-p" in args:
        plt.show(block=True)
except Exception as e:
    # print(f"ERROR: {e}")
    print(full_stack())
    os.makedirs(os.path.dirname(args["-o"]), exist_ok=True)
    with open(args["-o"]+".csv","w") as csv:
        csv.write("")