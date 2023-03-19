import time

from classes.input import parse_net,parse_arguments
from classes.circuit import Circuit
from classes.output import Output
from classes.terms import Terms

start=time.process_time()

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
circuit.calc_matrix()
print(circuit)
print("Calculating variables")
output.calc_variables()
print("Save CSV file")
output.save_csv(path)


print(time.process_time()-start)