"""2017. By Joshua Fitzgerald; Unix/MacOS capability by Jimmy Thrasher.

This program is the reference implementation of the Integ language, version 1.1.

In Integ, the only datatype is the integer. The variables have consecutive addresses in Integ (they may or may not be consecutive in memory) and do not get distinct names. Instead,
they are accessed with the notation {x and written to with the notation }xy where x is the address number and y is the new integer. y is optional;
the program will write 0 to x if y is empty.

Variables are declared in two ways; the variable is always initialized at the same time. 
The first declaration method, explicit declaration, occurs simply when a program tries to write to a previously unused address.
So, for instance, a program evaluating }(1)() when storage for address 1 has not yet been allocated will set aside storage for address 0 and set it equal to 0.
Similarly, a program evaluating }(5)(7) will set aside storage for address 5 and set it equal to 7.

In the second case: 

0 1 2 3 4 5
          ^
          7     

The second declaration method, implicit declaration, occurs when a program tries to set aside storage for an address that has empty positions between it and the
nearest address. For instance, a program evaluating }(5)(7) will not just set aside storage for address 5 and set it equal to 7, but also, if the nearest declared address
is 3, set aside storage for 4 and set it equal to 0.

To embed anything inside an operator, use (x). For example, }({(1))() will read from location 1 and write 0 at the location at one's contents. (x) is not counted
as an operator, but as a syntax feature.

Note that addresses cannot be read from unless they have been declared. The @ operator, which is of the form @(x) where x is a dummy argument, provides the maximum
assigned address to help with storage allocation. If no storage has been allocated, @ outputs -1.
Also note that address numbers must be greater than or equal to 0.

To deallocate storage, use _x. _x will deallocate all storage between the maximum allotted storage address and the address x, so be careful using it.
For example, if 0, 1, and 2 are allocated addresses, _(1) will deallocate 1 and 2, so that the only valid address will become 0.

Integer constants exist in Integ.

Things can be added and subtracted with + and -, and multiplied and divided with * and /. The modulus operator is %.

To print characters, use ]x. This operator prints a numeric code equal to the value of its contents.
To input a character code from the standard input, use [x. Note that [x does not wait for a newline,
and that its implementation may be platform dependent. As a result, this code may not work perfectly
on non-Windows platforms.

To output the current time in seconds since the beginning of the epoch, use "x, where x is a dummy argument. The returned time is rounded down.

To obtain a random number between x and y, use `xy, where x and y are the bounds for the random number. x and y do not have to be in any particular order;
`(0)(10) and `(10)(0) both work. Note that random number generation is intentionally implementation dependent; that way, the implementation determines the level
of randomness used. Note, then, that the implementation is responsible for providing the actual generator and a seed (if your generator is pseudo-random). This
reference implementation uses the Python random module, which is pseudo-random, and its default seed generation settings.

The conditional operator is of the form ?xyz. If x is 0, y will be evaluated; otherwise,
z will be evaluated.

The loop operator is of the form ~xy. While x is 0, y will be evaluated.

All operators must have one constitutent character, with the operands following in parentheses.
The character used must be distinct from all other operators' characters.

Comments are of the form #.x.#, where x can be basically anything. Comments don't nest; however, if the last part of your program is a comment, you can safely leave
off the end of the comment so that it becomes #.x; however, you cannot do x.# at the beginning of a program. Comments are removed before parsing.

$ can be used within the interactive prompt only to exit. Also note that $ is not an operator, so you can simply write $.
"""

import sys, time, random

# from http://code.activestate.com/recipes/134892/
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getche()


getch = _Getch()

global numarray #This is the big array that everything reads from.
numarray = [] #Nothing stored in it yet.

def write(arguments):
    """The function that corresponds to the { operator. Takes a list; returns the number written"""
    address = int(arguments[0])
    contents = int(arguments[1])
    maxpos = len(numarray) - 1 #The maximum position in the array.

    if address < 0: #We cannot use negative positions.
        print("\nCannot assign negative addresses.")
        sys.exit()
    
    while maxpos < address: #Declaring the storage we need, implicitly and explicitly
        numarray.append(0)
        maxpos += 1

    numarray[address] = contents #Actually writing the info
    return contents

def read(arguments):
    """The function that corresponds to the } operator. Takes a list; returns the number read"""
    address = int(arguments[0]) #We trust that parse did its job and properly provided the arguments.
    maxpos = len(numarray) - 1 #The maximum position in the array.

    if address < 0 or address > maxpos: #We cannot use negative positions.
        print("\nInvalid address " + str(address) + ".")
        sys.exit()
        
    return numarray[address]

def dealloc(arguments):
    """The function that corresponds to the _ operator. Takes a list; deallocates all addresses between the maximum address and a specified address and returns the address specified."""
    address = int(arguments[0])
    maxpos = len(numarray) - 1 #The maximum position in the array.

    if address < 0 or address > maxpos: #We cannot use negative positions.
        print("\nInvalid address " + str(address) + ".")
        sys.exit()
        
    del numarray[address : maxpos + 1] #Slicing is weird

    return address
    
def maxa(arguments):
    """The function that corresponds to the @ operator. Takes a dummy list; returns the maximum assigned storage address."""
    return len(numarray) - 1

def printer(arguments):
    """The function that corresponds to the ] operator. Takes a list; returns its contents."""
    try:
        #from https://stackoverflow.com/questions/25368786/python-print-does-not-work-in-loop
        #fixes glitch in shell with loop printing
        sys.stdout.write(chr(int(arguments[0])))
        sys.stdout.flush()
    except UnicodeEncodeError:
        pass #We would just print the standard box character that denotes missing
             #character if the character cannot be printed, but that's missing.
             #As a result, we ignore printing the character and just hope no one notices.
    except ValueError:
        pass #This is probably not great practice.
    return arguments[0]

def inputer(arguments):
    """The function that corresponds to the [ operator.
       Takes a dummy list; returns a character code where the character is from the standard input."""

    return ord(getch())

def add(arguments):
    """The function that corresponds to the + operator. Takes a list; returns the sum of its operands."""
    return int(arguments[0] + arguments[1])

def subtract(arguments):
    """The function that corresponds to the - operator. Takes a list; returns the difference between the first and second operands."""
    return int(arguments[0] - arguments[1])

def multiply(arguments):
    """The function that corresponds to the * operator. Takes a list; returns the product of its operands."""
    return int(arguments[0] * arguments[1])

def divide(arguments):
    """The function that corresponds to the / operator. Takes a list; returns the quotient the first and second operands."""
    if not arguments[1]:
        print("\nCannot divide by zero.")
        sys.exit()
    return int(arguments[0] / arguments[1])

def modulus(arguments):
    """The function that corresponds to the % operator. Takes a list; returns the remainder of the quotient of the first and second operands."""
    if not arguments[1]:
        print("\nCannot divide by zero.")
        sys.exit()
    return int(arguments[0] % arguments[1])

def inttime(arguments):
    """The function that corresponds to the " operator, Takes a list; returns the time in seconds since the start of the epoch, rounded down."""
    return int(time.time())

def randomint(arguments):
    """The function that corresponds to the ` operator. Takes a list (namely, the bounds; they do not have to be in order)
    and returns the random number between the bounds, inclusive."""
    if arguments[0] > arguments[1]:
        return random.randint(arguments[1], arguments[0])
    return random.randint(arguments[0], arguments[1])

def conditional(arguments):
    """conditional is a dummy function for ?. metaparse handles conditional execution."""
    if arguments:
        return arguments[0]

def loop(arguments):
    """conditional is a dummy function for ~. metaparse handles loop execution."""
    if arguments:
        return arguments[0]

def parse(inputstr, opconst):
    """Parses an input string according to the operator character list opconst
       and outputs, in this order, the operator, the operands, and anything else. The number of repeated
       characters in opconst determines whether an operator is unary, binary, tertiary, etc."""

    inputstr = inputstr.replace(" ", "") #Removes all notable types of whitespace
    inputstr = inputstr.replace("\n", "")
    inputstr = inputstr.replace("\t", "")
    
    opconst0 = "" #Gets first characters of operators
    for i in opconst:
        opconst0 += i[0]

    j = 0
    pos = 0 #The current position in the string
    
    operator = None

    if inputstr[0] == ")" or inputstr[0] == "(":
        print("\nError: Illegal use of ().")
        sys.exit()
    for i in opconst0: #Gets the operator type
        
        if i == inputstr[0]:
            operator = opconst[j]
            pos += 1
            break
        
        j += 1

    if inputstr[0] == "$":
        print("\n$ is not an operator; type it by itself in the interactive shell to exit.")
        sys.exit()
    
    if not operator: #We should have found an operator.
        print("\nOperator " + inputstr[0] + " not found.")
        sys.exit()
    lparen = rparen = tlp = trp = 0 #The first two are reset every argument; the last two stick around 

    j = 0

    args = []
    
    while j < len(operator): #Now we use j to get the arguments
        
        temparg = ""
        lparen = rparen = 0

        if pos > (len(inputstr) - 1):
            break
        
        for i in inputstr[pos:]: #Getting the arguments
            
            if lparen > rparen and (i != ")" or lparen - 1 != rparen):
                #Only add the character if the parentheses are still unbalanced. Do not add parentheses
                #that balance the parentheses
                temparg += i

            if lparen == rparen and lparen: #If the parentheses are balanced and exist:
                break

            if not lparen and not rparen and i != "(" and i != ")" and len(args) < len(operator):
                print("\nMore operands expected.")
                sys.exit()
            if i == "(":
                lparen += 1
                tlp += 1
        
            if i == ")":
                rparen += 1
                trp += 1
                
            pos += 1

        if len(args) < len(operator): #We don't want extra arguments
            args.append(temparg)
        else:
            break

        
        j += 1

    if len(args) < len(operator):
        print("\nMore operands expected.")
        sys.exit()
    if tlp != trp: #If the parentheses were never balanced completely in the string
        print("\nParentheses not balanced.")
        sys.exit()
    return [operator, args, inputstr[pos:]] #We return the operator, its arguments, and anything left in the string.

def metaparse(inputstring, operators):
    """metaparse is responsible for making parse helpful. parse separates a string into its components,
       and metaparse is responsible for using parse and figuring out how those components work together.
       Unlike parse, metaparse takes a dictionary with keys as parse-formatted operator strings and
       values as functions that metaparse must call. metaparse passes the keys to parse."""

    remainder = ""
    
    if not inputstring: #Returns 0 if the string is empty.
        return 0, remainder
    
    integer = 0
    try: #We try to convert the input string into an integer and return the integer. If that fails,
         #We know that we need to parse the input more.
        integer = int(inputstring)
        return integer, remainder
    except ValueError:
        pass

    output = parse(inputstring, list(operators.keys())) #Get and unpack parse output
    op = output[0]
    arguments = output[1]
    remainder = output[2]

    function = operators[op] #The function to be executed from the operator
    parsedvals = [] #parsing the arguments

    if op == "???": #metaparse directly works with the conditional operator
        
        if metaparse(arguments[0], operators)[0] == 0:
            parsedvals.append(metaparse(arguments[1], operators)[0])
            
        else:
            parsedvals.append(metaparse(arguments[2], operators)[0])
        
    elif op == "~~": #metaparse works directly with the loop operator
        
        while metaparse(arguments[0], operators)[0] == 0:
            parsedvals.append(metaparse(arguments[1], operators)[0])
    
    else: #everything else ultimately goes through functions
        for i in arguments:
            parsedvals.append(metaparse(i, operators)[0])

    out = function(parsedvals)
    if remainder:
        out = metaparse(remainder, operators)
    return out, remainder

def nocomments(input):
    """nocomments removes comments, which are of the form #.<comment_text>.# and which do not nest.
       You don't have to put a comment end signifier if you want the last bit of the program to be a comment."""
    incomment = False
    lastchar = None
    output = ""
    for i in input: #Basically, just add characters to the output if they aren't in comments in the input.
        if i == "." and lastchar == "#" and incomment == False:
            incomment = True
        if i == "#" and lastchar == "." and incomment == True:
            incomment = False
                    
        if not incomment and i != "#" and i != ".":
          output += i

        lastchar = i
    
    return output

#The main body of the interpreter--almost like a metametaparse function

string = "" #The actual program is stored here
opdict = {"}}" : write, "{" : read, "_" : dealloc, "@" : maxa, "]" : printer, "[" : inputer, "++" : add, "--" : subtract,
          "**" : multiply, "//" : divide, "%%" : modulus, "\"" : inttime, "``" : randomint, "???" : conditional, "~~" : loop}
                                             #These are the operators currently supported by Integ. The number
                                             #of times that the character is repeated is the number of operands
                                             #that the operator requires. Each operator (except for the conditional and loop operators)
                                             #maps to a function that
                                             #performs its task.

if (sys.stdin.isatty()):
    print("""
--------Integ 1.1---------
 Interactive  Interpreter""")
    while True: #interactive interpreter
        
        print("\n")
        string = input(">>> ")
        if string == "$":
            break
        try:
            metaparse(nocomments(string), opdict)
        except SystemExit:
            pass #We don't want to exit when there's an error.
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt.")
            continue
else:
    while True: #collecting input for redirection-type input
        try:
            string += input()
        except EOFError:
            break
    try:    
        metaparse(nocomments(string), opdict)
        
    except KeyboardInterrupt:
            print("\nKeyboard Interrupt.")
            
