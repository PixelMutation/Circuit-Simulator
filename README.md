# Cascade Circuit Simuator  

## Prerequesites:
sympy numpy matplotlib
## Examples
### Autotester
```python .\AutoTest_08.py .\analyse_circuit.py 1e-13 1e-13```  
Runs through nets in ./User_files/ and compares the resulting .csv to those in ./Model_files/  
Console output for these tests written to .log files
### Plotting
Plots are saved as netname_column.png in the output path, and displayed using the -d flag, for example:  
`python .\analyse_circuit.py .\User_files\Ext_e_Ladder_400 -p [2,3] -d`

## Syntax
### Usage:  
`python analyse_circuit.py input_path output_path optional_args`  
   `python analyse_circuit.py input_path optional_args`  
    `python analyse_circuit.py optional_args`   
### Optional Arguments:  
   `-i input_path`       e.g. nets/b_CR.net  Sets input path (suffix not required)  
   `-o output_path`      e.g. out/b_CR.csv   Sets the output path, uses input path if not set  
   `-p columns_list`     e.g. [2,3,4]        Plots the listed columns from the CSV, saves PNG to output path  
   `-d`                                      Displays the plots in an interactive window  
## Console / log output
Program section, duration and object contents are  printed to the console.  
An ASCII circuit diagram is also printed
## Variables
New output variables can be added by adding them to variables.py  
This includes creating a new Sympy symbol, adding to the conversion table, adding the equation and adding the corresponding dependencies