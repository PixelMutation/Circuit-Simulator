from sympy import Symbol

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

Freq   = Symbol("Freq"   ) 

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