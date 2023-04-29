import time

from classes.input import parse_net,parse_arguments
from classes.circuit import Circuit
from classes.output import Output
from classes.terms import Terms

start_process=time.process_time_ns()

args=parse_arguments()
path=args["-i"].replace(".net","")

# Utility function for printing and timing each section of the program
start_section=None
def startSection(name):
    global start_section
    # Print duration of previous section (if not currently in first section)
    if not start_section is None:
        print(f"# Section took {((time.process_time_ns()-start_section)/(10**9)):.3f}s ")
    print(name.center(70,"-"))
    start_section=time.process_time_ns()
    
startSection("Reading Net File")
circuit_dicts,terms_dict,output_dict=parse_net(path)

startSection("Creating Terms object")
terms=Terms(terms_dict)
print(terms)

startSection("Creating Circuit object")
circuit=Circuit(circuit_dicts,terms)
print(circuit)

startSection("Creating Output Object ")
output=Output(output_dict,circuit,terms)
# print(output)

startSection("Calculating ABCD matrices")
circuit.calc_component_ABCDs()

startSection("Combining ABCD matrices")
circuit.calc_overall_ABCDs()

startSection("Calculating variables")
output.calc_variables() # Requests each var to be calculated by circuit class

startSection("Formatting variables")
output.convert_variables() # Converts each value to chosen units and stores inside Column object

startSection("Saving output as CSV")
output.save_csv(path) # Convert column objects to CSV

plot=False
if plot:
    startSection("Generating plots against frequency")
    output.generate_plots()
    if output.plot_show:
        startSection("Displaying plots")
        output.display_plots()

startSection("END")
print(f"Program took {((time.process_time_ns()-start_process)/(10**9)):.2f}s (process time)")