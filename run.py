from solve import solve, Grid_List

# Run this code #
#filename = 'incomplete.txt'

solved = solve()
#print "Solution:\n"
#for row in Grid_List[-1].value:
#    print "{}".format(row)

if solved[0]:
    with open("solution.txt","w") as text_file:
        for row in Grid_List[-1].value:
            for i,element in enumerate(row):
                text_file.write(str(element))
                if i == len(row)-1:
                    text_file.write("\n")
                else:
                    text_file.write(" ")
