from main_app.file_utilities import *
import subprocess
import os
import shutil


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

        cmd = adb_location + space + cmd + space + get_app_repo_location() + space + repo_location

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
            correct = ''
            while (correct != 'y') and (correct != 'n'):
                correct = input('Are you absolutely sure you want to DELETE ALL FILES in (y=yes, n=no): '
                                + repo_location + "\r\n")
            if correct == 'y':
                for curr_path in os.listdir(repo_location):
                    file_path = os.path.join(repo_location, curr_path)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(e)
            else:
                return False
        return True
