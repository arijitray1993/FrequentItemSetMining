# Python code for frequent item-set mining

Description: Mine co-occuring items in a list of transactions with frequency greater than support parameter, sigma, and item set size greater than another parameter, N. 

## How to run code:

`python analyze2.py --sigma <sigma> --N <N>`

`<sigma>` and `<N>` are integers like 4 and 3 respectively. 

If you just run python analyze2.py without any arguments, it runs with a default of sigma=4 and N=3. 

Hence,

`python analyze2.py --sigma 4 --N 3` 

and

`python analyze2.py` 

have the same result. 

Make sure the input file is named `retail_25k.dat`. 

Output will be auto-saved in a file named `output_25k.dat`. 

While the program in running, a number will be displayed that corresponds to the length of the frontier yet to be explored. The closer that is to 0, the closer the analysis is to completion. 

Note: The analysis for retail_25k.dat takes about 260 MB of RAM. 
