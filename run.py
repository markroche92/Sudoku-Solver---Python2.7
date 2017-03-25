from solve import solve
from classes import Grid

# Run this code #

solved = solve()
for row in Grid.value:
    print "{}".format(row)

if solved:
    with open("solution.txt","w") as text_file:
        for row in Grid.value:
            for i,element in enumerate(row):
                text_file.write(str(element))
                if i == len(row)-1:
                    text_file.write("\n")
                else:
                    text_file.write(" ")
