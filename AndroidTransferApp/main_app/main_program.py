import os
import shutil
import subprocess
import platform

system_name = platform.system()
base_location = os.path.dirname(os.path.realpath(__file__))
SLASH = '/'
if system_name == 'Linux':
    # TODO: ADD THESE TO THE 'STATIC' FILES, LIKE PROMPT.TXT
    SLASH = '/'
    ADB_ENDING = 'adb'
    ADB_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__)) + SLASH + 'previous_adb_location.txt'
    REPO_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__)) + SLASH + 'previous_repo_location.txt'
else:
    SLASH = '\\'
    ADB_ENDING = 'adb.exe'
    ADB_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__)) + SLASH + 'previous_adb_location.txt'
    REPO_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__)) + SLASH + 'previous_repo_location.txt'

APP_REPO_LOCATION = 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'


def read_from_adb_file():
    if not os.path.isfile(ADB_FILE_LOCATION):
        print('Must specify a new adb file location if no previous record of one exists. Not enough parameters')
        return None

    try:
        adb_file = open(ADB_FILE_LOCATION, 'r')
        adb_location = adb_file.readline()
        adb_file.close()
        if adb_location == '':
            print('No adb location on record')
            return None
        return adb_location
    except Exception as e:
        print('Could not read adb record file because of the following exception:')
        print(e)
        return None


def read_from_repo_file():
    if not os.path.isfile(REPO_FILE_LOCATION):
        print('Must specify a new destination for the transferred files if no record of one exists.',
              'Not enough parameters.')
        return None

    try:
        repo_file = open(REPO_FILE_LOCATION, 'r')
        repo_location = repo_file.readline()
        repo_file.close()
        if repo_location == '':
            print('No file repository location on record')
            return None
        return repo_location
    except Exception as e:
        print('Could not read transfer repository record file because of the following exception:')
        print(e)
        return None


def write_to_adb_file(new_adb_location):
    if not os.path.isdir(new_adb_location):
        print('New path to adb location is not a valid directory/path.',
              'Please retry with a valid path to the adb file')
        return None

    try:
        new_adb_location = new_adb_location + SLASH + ADB_ENDING
        adb_file = open(ADB_FILE_LOCATION, 'w')
        adb_file.write(new_adb_location)
        adb_file.close()
        return new_adb_location
    except Exception as e:
        print('Could not read adb record file because of the following exception:')
        print(e)
        return None


def write_to_repo_file(new_repo_location):
    if not os.path.isdir(new_repo_location):
        print('New path to transfer file repository is not a valid directory/path.',
              'Please retry with a valid path to the directory you wish to transfer files to.')
        return None

    try:
        repo_file = open(REPO_FILE_LOCATION, 'w')
        repo_file.write(new_repo_location)
        repo_file.close()
        return new_repo_location
    except Exception as e:
        print('Could not read transfer repository record file because of the following exception:')
        print(e)
        return None


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
        num_params = len(self.params)

        if num_params == 0:
            adb_location = read_from_adb_file()
            if adb_location is None:
                return False
            repo_location = read_from_repo_file()
            if repo_location is None:
                return False

        elif len(self.params) == 2:
            if self.params[0] == '-a':
                adb_location = write_to_adb_file(self.params[1])
                if adb_location is None:
                    return False
                repo_location = read_from_repo_file()
                if repo_location is None:
                    return False
            elif self.params[0] == '-r':
                repo_location = write_to_repo_file(self.params[1])
                if repo_location is None:
                    return False
                adb_location = read_from_adb_file()
                if adb_location is None:
                    return False
            else:
                adb_location = write_to_adb_file(self.params[0])
                if adb_location is None:
                    return False
                repo_location = write_to_repo_file(self.params[1])
                if repo_location is None:
                    return False
        else:
            print("Incorrect number of parameters. Only zero or two parameters expected.")
            return False

        cmd = 'pull'

        space = ' '

        cmd = adb_location + space + cmd + space + APP_REPO_LOCATION + space + repo_location

        try:
            p1 = subprocess.Popen(cmd.split())
            time_wait = 60
            if len(self.params) > 1:
                try:
                    time_wait = int(self.params[1])
                except ValueError:
                    print("Error processing timeout parameter - continuing with timeout of 10 seconds.")
                    time_wait = 10
            p1.wait(time_wait)

        except Exception as e:
            print(
                "Error using adb to transfer.",
                "Possibly due to phone not being connected.",
                "Please check connection and phone access permissions.",
                "The exact error that occurred is as follows:")
            print(e)
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
        repo_location = read_from_repo_file()
        if repo_location is None:
            print('No previous transfer repository location on record. Did not clear.')
            return False

        if os.path.exists(repo_location):
            for curr_path in os.listdir(repo_location):
                file_path = os.path.join(repo_location, curr_path)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)

        return True


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

    f = open(os.path.dirname(os.path.realpath(__file__)) + '/prompt.txt', 'r')
    for line in f:
        print(line)
    print('\n')
    f.close()

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


if __name__ == "__main__":
    main()
