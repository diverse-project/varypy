# varypy

Executing Python programs/projetcs in multiple environments (varying Python versions, libraries' versions, etc.) 

`varypy XXX.py` will synthesize multiple (virtual) Python environments and execute a given program in these different environments. 
The outcome will be a report on actual executions (pass/failures + results/traces of the executions/failures) on the different environments. 
Some recommendations will be given eg don't use this Python version, don't use this library with this Python version, use this library version > 1.y, or use this specific set of versions to improve your performance, energy consumption, or accuracy. 
A sensitivity analysis of the considered program with regards to variability in the computing environment is also planned. 
In short, the goal of `varypy` is to replace `python` ;)  

`varypy` can take as input:
 * the location of a Python program
 * an URL of a git repo
 * the location of a Python notebook 
 * the location of a directory 

+ some (optional) instructions on what to execute (eg test suite, benchmark, main program)

`varypy` internally uses either/or:
 * `pipenv` 
 * `poetry`
 * `Docker` 

For more information about the project in its actual state you can check out : 
![INFO.md](INFO.md)