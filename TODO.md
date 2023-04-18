# Main tasks
- [x] Add prefix support to inputs
- [x] Make decibels / rads display correctly in output heading
- [ ] Add equations for other variables
- [ ] Store raw (SI unit) values calculated so far in circuit class
    - [ ] Automatically calculate (but not write to csv) prerequesite values (e.g. Av, Ai* for Ap) 
    - [ ] Prevent these values from being recalculated
    - [ ] Use empty dict storing None until values populated
- [ ] Fix output orders 
- [ ] Add multiprocessing for calculating at frequencies
    - [ ] divide list into n sections
    - [ ] spawn an evaluate() process for each sub list
- [x] Implement numpy array processing
- [ ] Error handling
- 


# New Branch  
substitute frequencies into each ABCD before multiplying, 
- [ ] makes final simplification easier
- [ ] might be slower for small circuits?
- [ ] since the combined ABCD matrix is too large to display, it seems to crash sympy? struggles to simplify at least
- [ ] Two stages:
    - [ ] Calculate combined ABCD for each freq, iterating through each component
    - [ ] Subsitute into equations and solve
- [ ] First thing to try would just be substituting the ABCD frequencies first, this may simplify enough to make the current system work
- [ ] Add format(varName) function to output which stores the chosen variable in the chosen format in the output_dict
    - [ ] Change calc_variables() to not perform this conversion
    - [ ] Add format_variables(), which uses format() on all chosen varibles
- [ ] Create custom CSV formatting function to replace library