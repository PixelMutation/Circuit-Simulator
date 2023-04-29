from sympy import Symbol,symbols,conjugate


# Possible output variables
Vin  = Symbol("Vin"  )
Vout = Symbol("Vout" )
Iin  = Symbol("Iin"  )
Iout = Symbol("Iout" )
Zin  = Symbol("Zin"  )
Zout = Symbol("Zout" )
Pin  = Symbol("Pin"  )
Pout = Symbol("Pout" )
Av   = Symbol("Av"   )
Ai   = Symbol("Ai"   )
Ap   = Symbol("Ap"   ) 

# Frequency variable
Freq   = Symbol("Freq"   ) 

# Table used to convert from strings to symbols
var_table={
    "Freq"  : Freq,
    "Vin"   : Vin,    
    "Vout"  : Vout,  
    "Iin"   : Iin,    
    "Iout"  : Iout,  
    "Zin"   : Zin,    
    "Zout"  : Zout,  
    "Pin"   : Pin,    
    "Pout"  : Pout,  
    "Av"    : Av,      
    "Ai"    : Ai,      
    "Ap"    : Ap,      
}

# Intermediate variables
A,B,C,D,VT,ZS,ZL=symbols("A,B,C,D,VT,ZS,ZL")
inv_A,inv_B,inv_C,inv_D=symbols("inv_A,inv_B,inv_C,inv_D")

# Sympy equations for each variable, to be converted to lambdas
# This allows any new variable to easily be defined
equations={
    Vin  :   Iin*Zin,
    Vout :   Vin*inv_A+Iin*inv_B,
    Iin  :   VT/(ZS+Zin),
    Iout :   Vin*inv_C+Iin*inv_D,
    Zin  :   (A*ZL+B)/(C*ZL+D),
    Zout :   (D*ZS+B)/(C*ZS+A),
    Pin  :   Vin*conjugate(Iin),
    Pout :   Vout*conjugate(Iin),
    Av   :   ZL/(A*ZL+B),
    Ai   :   1 /(C*ZL+D),
    Ap   :   Av*conjugate(Ai),
}

# Stores the dependencies of each variable that must be calculated first
dependencies={
    Vin     : [Iin,Zin],
    Vout    : [Vin,Iin,inv_A,inv_B],
    Iin     : [VT,ZS,Zin],
    Iout    : [Vin,inv_C,Iin,inv_D],
    Zin     : [A,B,C,D,ZL],
    Zout    : [A,B,C,D,ZS],
    Pin     : [Vin,Iin],
    Pout    : [Vout,Iin],
    Av      : [A,B,C,ZL],
    Ai      : [B,C,D,ZL],
    Ap      : [Av,Ai],
}