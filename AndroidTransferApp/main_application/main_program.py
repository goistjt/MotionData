import os
import shutil
import subprocess

APP_REPO_LOCATION = 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'


def get_android_route():
    return os.path.dirname(os.path.realpath(__file__)) + "/android_files"


class Command:
    def __init__(self, params):
        self.params = params

    def execute(self):
        pass


class UpdateAndroidCache(Command):
    def __init__(self, params):
        Command.__init__(self, params)

    def execute(self):

        if (len(self.params) > 0) and (self.params[0] is not None):
            adb_location = self.params[0]

        else:
            return False

        repository_dir_location = get_android_route()

        if not os.path.exists(get_android_route()):
            os.makedirs(get_android_route())

        if not os.path.isfile(adb_location):
            print("Give adb location does not exist.")
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
    def __init__(self, params):
        Command.__init__(self, params)

    def execute(self):

        if os.path.exists(get_android_route()):
            try:
                shutil.rmtree(get_android_route())

            except OSError as e:
                print(e)
                return False

        return True


COMMAND_DICTIONARY = {
    "update": UpdateAndroidCache,
    "clear": ClearAndroidCache
}

if __name__ == "__main__":

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
            try:
                command_class = COMMAND_DICTIONARY[split_by_space[0]]
            except KeyError:
                print("Invalid command type. Please check the name and try again.")
                continue

            success_flag = command_class(split_by_space[1:]).execute()

            if not success_flag:
                print("Command failed. Please reference error and retry.")
                continue

            print("Command succeeded!")
