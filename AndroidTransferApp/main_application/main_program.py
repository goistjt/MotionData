import os
import shutil
import subprocess
import platform

APP_REPO_LOCATION = 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'


def get_android_route():
    """
    :returns location of the android cache (the directory transferred files will be placed into.
    """
    system_name = platform.system()
    base_location = os.path.dirname(os.path.realpath(__file__))
    if system_name == 'Linux':
        return base_location + '/android_files'
    else:
        return os.path.dirname(os.path.realpath(__file__)) + '\\android_files'


class Command:
    """
    The base interface command, specifying the 'execute' method.
    """
    def __init__(self, params):
        self.params = params

    def execute(self):
        """
        :returns True - it always succeeds
        """
        return True


class UpdateAndroidCache(Command):
    """
    Updates the Android cache using the adb location specified to perform the transfer subprocess.
    """
    def __init__(self, params):
        Command.__init__(self, params)

    def execute(self):
        """
        Needs exactly one parameter - will return False if there is not at least one parameter given. Any extra
        parameters will be ignored.
        :returns the success of the transfer action in total
        """
        if (len(self.params) > 0) and (self.params[0] is not None):
            adb_location = self.params[0]

        else:
            return False

        repository_dir_location = get_android_route()

        if not os.path.exists(get_android_route()):
            os.makedirs(get_android_route())

        if not os.path.isfile(adb_location):
            print("Given adb location does not exist.")
            return False

        cmd = 'pull'

        space = ' '

        cmd = adb_location + space + cmd + space + APP_REPO_LOCATION + space + repository_dir_location

        try:
            p1 = subprocess.Popen(cmd.split())
            time_wait = 10
            if len(self.params) > 1:
                try:
                    time_wait = int(self.params[1])
                except ValueError:
                    print("Error processing timeout parameter - continuing with timeout of 10 seconds.")
                    time_wait = 10
            p1.wait(time_wait)

        except subprocess.CalledProcessError:
            print(
                "Error using adb to transfer.",
                "Possibly due to phone not being connected.",
                "Please check connection and phone access permissions.")
            return False

        return True


class ClearAndroidCache(Command):
    """
    The command class used to delete the contents of the Android cache
    """
    def __init__(self, params):
        Command.__init__(self, params)

    def execute(self):
        """
        Uses the existing parameters to recursively delete all contents.
        :returns the success of the deletions in total
        """
        if os.path.exists(get_android_route()):
            try:
                shutil.rmtree(get_android_route())

            except OSError as e:
                print(e)
                return False

        return True


"""
This dictionary holds the command types and the keyword associated to each type for the interface to use
"""
COMMAND_DICTIONARY = {
    "update": UpdateAndroidCache,
    "clear": ClearAndroidCache
}

if __name__ == "__main__":
    """
    Starting prompt describing what this app can accomplish and how to perform the two actions.
    """

    print("Transfer Application Interface Started!\n")
    print("***Please note that every space character used in these commands is",
          "considered a parameter delimiter, or the differentiation character between inputs of methods.***\n")
    print("Steps:")
    print("1. Plug the Android device you wish to transfer from, via usb, into your computer.\n")
    print("2. To 'update' the Android cache by transferring the",
          "files from the phone to the computer, type this command:")
    print("update <the location of the adb, or 'Android Debug Bridge' installation>\n")
    print("3. To 'clear' the Android cache by deleting all files",
          "stored in the designated transfer directory, type this command:")
    print("clear")
    print("[the clear command has no parameters, but will attempt to clear regardless,",
          "ignoring the 'parameters' given]\n")

    """
    The below is the main interface loop. It prints a prompt, takes a line of input, and separates the parameters by
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
