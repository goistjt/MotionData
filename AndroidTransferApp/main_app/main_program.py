from main_app.commands import *

"""
This dictionary holds the command types and the keyword associated to each type for the interface to use
"""
COMMAND_DICTIONARY = {
    "update": UpdateAndroidCache,
    "clear": ClearAndroidCache
}


def main():
    """
    Starting prompt.txt describing what this app can accomplish and how to perform the two actions.
    """

    print_prompt()

    """
    The below is the main interface loop. It prints a prompt.txt, takes a line of input, and separates the parameters by
    a space delimiter, crating the appropriate command object type based on the input's starting word, passing in all
    other parameters.
    """

    while True:

        user_input = input("CMD>")

        if (user_input is None) or (user_input == '' or user_input[0] == " "):
            print("Invalid input. Please try again.")
            continue

        split_by_space = user_input.split(' ')

        if split_by_space[0] == "quit":
            print("Exiting application.")
            break

        else:
            if split_by_space[0] in COMMAND_DICTIONARY.keys():
                command_class = COMMAND_DICTIONARY[split_by_space[0]]

            else:
                print("Invalid command type. Please check the name and try again.")
                continue

            success_flag = command_class(split_by_space[1:]).execute()

            if not success_flag:
                print("Command failed. Please reference error and retry.")
                continue

            print("Command succeeded!")
