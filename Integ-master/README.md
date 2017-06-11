# Integ

Note: You need Python 3 to run the Integ interpreter.

Integ is an esoteric programming language in which the only datatype is the integer and the only storage is one large, variable-length array of integers which is accessed through non-negative addresses, beginning at 0. In Integ, variables do not get distinct names. Instead, they are accessed with the notation {x and written to with the notation }xy where x is the address number and y is the new integer. y is optional; the program will write 0 to x if y is simply a set of empty parentheses (see below).

Variables are declared in two ways; the variable is always initialized at the same time.

The first declaration method, explicit declaration, occurs simply when a program tries to write to a previously unused address.
So, for instance, a program evaluating }(1)() when storage for address 1 has not yet been allocated will set aside storage for address 0 and set it equal to 0. Similarly, a program evaluating }(5)(7) will set aside storage for address 5 and set it equal to 7.

The second declaration method, implicit declaration, occurs when a program tries to set aside storage for an address that has empty positions between it and the nearest address. For instance, a program evaluating }(5)(7) will not just set aside storage for address 5 and set it equal to 7, but also, if the nearest declared address is 3, set aside storage for 4 and set it equal to 0.

To embed anything inside an operator, use (x). For example, }({(1))() will read from location 1 and write 0 at the location at one's contents. (x) is not counted as an operator, but as a syntax element. Empty () are automatically 0.

Note that addresses cannot be read from unless they have been declared. The @ operator, which is of the form @(x) where x is a dummy argument, provides the maximum
assigned address to help with storage allocation. If no storage has been allocated, @ outputs -1.
Also note that address numbers must be greater than or equal to 0.

To deallocate storage, use _x. _x will deallocate all storage between the maximum allotted storage address and the address x, so be careful using it.
For example, if 0, 1, and 2 are allocated addresses, _(1) will deallocate 1 and 2, so that the only valid address will become 0.

Decimal integer constants exist in Integ.

Things can be added and subtracted with + and -, and multiplied and divided with * and /. For instance, +(2)(3) is 5; -(2)(3) is -1; \*(2)(3) is 6; /(2)(3) is 0, as division is rounded down to the nearest integer. The interpreter catches division by zero errors.

To print characters, use ]x. This operator prints the character equivalent to x. For example, ](97) prints "a".
To input a character from the standard input and receive its character code, use [x, where x is a dummy argument. Note that invalid codes will simply be ignored. [ does not work in IDLE; use a command line interface instead.

To output the current time in seconds since the beginning of the epoch, use "x, where x is a dummy argument. The returned time is rounded down.

To obtain a random number between x and y, use \`xy, where x and y are the bounds for the random number. x and y do not have to be in any particular order;
\`(0)(10) and \`(10)(0) both work. Note that random number generation is intentionally implementation dependent; that way, the implementation determines the level
of randomness used. Note, then, that the implementation is responsible for providing the actual generator and a seed (if your generator is pseudo-random). This
reference implementation uses the Python random module, which is pseudo-random, and its default seed generation settings.

The conditional operator is of the form ?xyz. If x is 0, y will be evaluated; otherwise,
z will be evaluated. For instance, ? (-(\[())(97)) (](97)) () prints "a" if it receives "a", and does not print anything if it receives another character.

The loop operator is of the form \~xy. While x is 0, y will be evaluated. For instance, }()()\~(0)(](}()(+({())(1)))](32)) will print the characters (or try to print the characters) with codes 0, 1, 2, 3, 4, 5... and so forth for infinity, or until the application is exited.

Tabs, spaces, and newlines are ignored; as a result, you can design your code in almost any shape.

Comments are of the form #.x.#, where x can be basically anything. Comments don't nest; however, if the last part of your program is a comment, you can safely leave off the end of the comment so that it becomes #.x; however, you cannot write x.# at the beginning of a program. Comments are removed before parsing.

$ can be used within the interactive prompt only to exit. Also note that $ is not an operator, so you can simply write $.

----
Examples
----

helloworld.int: Prints "hello, world".

numiter.int: Prints numbers 0-9 forwards and backwards endlessly.

say_a.int: Wants you to press "a" over and over and over. This program does not work in the Python IDLE; try a command prompt instead.
