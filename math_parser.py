import math
import numpy as np

_CONSTANTS = {
    'pi' : math.pi,
    'e' : math.e,
    'phi': (1 + 5 ** .5) / 2
}

_FUNCTIONS = {
    'abs': np.abs,
    'ceil': np.ceil,
    'cos': np.cos,
    'cosh': np.cosh,
    'degrees': np.degrees,
    'exp': np.exp,
    'fabs': np.fabs,
    'floor': np.floor,
    'fmod': np.fmod,
    'frexp': np.frexp,
    'ldexp': np.ldexp,
    'log': np.log,
    'log10': np.log10,
    'modf': np.modf,
    'radians': np.radians,
    'sin': np.sin,
    'sinh': np.sinh,
    'sqrt': np.sqrt,
    'tan': np.tan,
    'tanh': np.tanh
}

class Parser:
    def __init__(self, string, vars = None):
        self.string = string
        self.index = 0
        self.vars = {} if vars == None else vars.copy()
        for constant in _CONSTANTS.keys():
            if self.vars.get(constant) is not None:
                raise Exception("Cannot redefine the value of " + var)

    def get_value(self):
        value = self.parse_expression()
        self.skip_whitespace()
        
        if self.has_next():
            raise Exception(
                "Unexpected character found: '" + self.peek() + "' at index " + str(self.index)
            )
        return value

    def peek(self):
        return self.string[self.index:self.index + 1]

    def has_next(self):
        return self.index < len(self.string)

    def skip_whitespace(self):
        while self.has_next():
            if self.peek() in ' \t\n\r':
                self.index += 1
            else:
                return

    def parse_expression(self):
        return self.parse_addition()
    
    def parse_addition(self):
        values = [self.parse_multiplication()]
        
        while True:
            self.skip_whitespace()
            char = self.peek()
            
            if char == '+':
                self.index += 1
                values.append(self.parse_multiplication())
            elif char == '-':
                self.index += 1
                values.append(-1 * self.parse_multiplication())
            else:
                break
        
        return sum(values)

    def parse_multiplication(self):
        values = [self.parse_parenthesis()]
            
        while True:
            self.skip_whitespace()
            char = self.peek()
                
            if char == '*':
                self.index += 1
                char = self.peek()
                if char == '*':
                    self.index += 1
                    power = self.parse_parenthesis()
                    values[-1] = values[-1]**power
                else:
                    #self.index += 1
                    values.append(self.parse_parenthesis())
            elif char == '/':
                div_index = self.index
                self.index += 1
                denominator = self.parse_parenthesis()
                     
                if denominator == 0:
                    raise Exception(
                        "Division by 0 kills baby whales (occured at index " + str(div_index) + ")"
                    )
                values.append(1.0 / denominator)
            else:
                break
                     
        value = 1.0
        
        for factor in values:
            value *= factor
        return value

    def parse_parenthesis(self):
        self.skip_whitespace()
        char = self.peek()
        
        if char == '(':
            self.index += 1
            value = self.parse_expression()
            self.skip_whitespace()
            
            if self.peek() != ')':
                raise Exception(
                    "No closing parenthesis found at character " + str(self.index)
                )
            self.index += 1
            return value
        else:
            return self.parse_negative()

    def parse_negative(self):
        self.skip_whitespace()
        char = self.peek()
        
        if char == '-':
            self.index += 1
            return -1 * self.parse_parenthesis()
        else:
            return self.parse_value()

    def parse_value(self):
        self.skip_whitespace()
        char = self.peek()

        if char in '0123456789.':
            return self.parse_number()
        else:
            return self.parse_variable()
 
    def parse_variable(self):
        self.skip_whitespace()
        var = []
        while self.has_next():
            char = self.peek()
            
            if char.lower() in '_abcdefghijklmnopqrstuvwxyz0123456789':
                var.append(char)
                self.index += 1
            else:
                break
        var = ''.join(var)
        
        function = _FUNCTIONS.get(var.lower())
        if function is not None:
            arg = self.parse_parenthesis()
            return np.asfarray(function(arg), float)
        
        constant = _CONSTANTS.get(var.lower())
        if constant is not None:
            return constant

        value = self.vars.get(var, None)
        if value is not None:
            return np.asfarray(value,float)
            
        raise Exception("Unrecognized variable: '" + var + "'")

    def parse_number(self):
        self.skip_whitespace()
        strValue = ''
        decimal_found = False
        char = ''

        while self.has_next():
            char = self.peek()            
            
            if char == '.':
                if decimal_found:
                    raise Exception(
                        "Found an extra period in a number at character " + str(self.index) + ". Are you European?"
                    )
                decimal_found = True
                strValue += '.'
            elif char in '0123456789':
                strValue += char
            else:
                break
            self.index += 1

        if len(strValue) == 0:
            if char == '':
                raise Exception("Unexpected end found")
            else:
                raise Exception(
                    "I was expecting to find a number at character " + str(self.index) + " but instead I found a '" + char + "'. What's up with that?")
        return np.asfarray(strValue,float)


def evaluate(expression, vars = None):
    #try:
    p = Parser(expression, vars)
    value = p.get_value()
    #except Exception as ex:
    #    msg = ex.message
    #    raise Exception(msg)
    
    return value

if __name__ == "__main__":
    print(evaluate("cos(x+4*3) + 2 * 3", {'x' : np.ones(5)*5., 'y' : np.ones(5)*5.}))
    print(evaluate("exp(0)"))
    print(evaluate("2**pi"))
    print(evaluate("-(1 + 2) * 3"))
    print(evaluate("(1-2)/3.0 + 0.0000"))
    print(evaluate("abs(-2) + pi / 4"))
    print(evaluate("(x + e * 10) / 10", { 'x' : 3 }))
    print(evaluate("1.0 / 3 * 6"))
    print(evaluate("(1 - 1 + -1) * pi"))
    print(evaluate("cos(pi) * 1"))
