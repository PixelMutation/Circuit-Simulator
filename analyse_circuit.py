import time

from classes.input import parse_net,parse_arguments
from classes.circuit import Circuit
from classes.output import Output
from classes.terms import Terms

start_process=time.process_time()

args=parse_arguments()
path=args["-i"].replace(".net","")

circuit_dicts,terms_dict,output_dict=parse_net(path)

print("Creating Terms object")
terms=Terms(terms_dict)
# print(terms)
print("Creating Circuit object")
circuit=Circuit(circuit_dicts,terms)
print("Creating Output object")
output=Output(output_dict,circuit,terms)
# print(output)
print("Calculating ABCD matrices")
circuit.calc_matrices()
print(circuit)
print("Calculating variables")
output.calc_variables() # Requests each var to be calculated by circuit class
print("Formatting variables")
output.format_variables() # Converts each value to chosen units and stores inside dict
print("Save CSV file")
output.save_csv(path) # Convert dict of format to CSV
if output.plot:
    print("Plotting chosen variables against frequency")
    output.generate_plots()
    if output.plot_show:
        print("Displaying plots")
        output.display_plots()


print(f"Program took {(time.process_time()-start_process):.2f}s (process time)")