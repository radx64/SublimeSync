import os
import shutil
import subprocess

import sublime
import sublime_plugin

def isGitInstalled():
    try:
        out = subprocess.check_output(["git", "--version"], shell=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

class SublimeSyncCommand(sublime_plugin.ApplicationCommand):
    def __init__(self):
        self.settings = None

    def get_setting(self, key):
            if self.settings is None:
                self.settings = sublime.load_settings(
                    "SublimeSync.sublime-settings")
            return self.settings.get(key)

    def set_setting(self, key, value):
            if self.settings is None:
                self.get_setting("")
            self.settings.set(key, value)
            self.settings = sublime.save_settings("SublimeSync.sublime-settings")

    def get_repository_url(self):
        return self.get_setting("repository_url")

    def get_credentials_repository_url(self):
        repository_url =  self.get_setting("protocol") + '://'
        repository_url += self.get_setting("username") + ':'
        repository_url += self.get_setting("token") + '@'
        repository_url += self.get_repository_url()
        return repository_url

    def get_branch_name(self):
        return self.get_setting("branch")

    def first_run(self):
        if len(self.get_repository_url()) == 0:
            sublime.error_message("Repository url is not set in settings file. Do it first, then run sync again")
            return

        if not self.get_setting('first_run'):
            return
        result = sublime.yes_no_cancel_dialog("Looks like it was first time You run Sublime Sync on this computer."
            + "\n\nRepository: "+ self.get_repository_url()
            + "\nBranch: "+ self.get_branch_name()
            + "\n\nWhat do you want to do first? ", "PULL (will overwrite current settings)",
            "PUSH (upload current settings to repository)")

        if result == sublime.DIALOG_CANCEL:
            return

        if result == sublime.DIALOG_YES:
            self.set_setting("first_run", False)
            git_pull()

        if result == sublime.DIALOG_NO:
            self.set_setting("first_run", False)
            git_push()

    def run_process(self, args, cwd):
        print(args)
        process = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdoutdata, stderrdata = process.communicate()

        print(stdoutdata.decode("utf-8"), end="")
        print(stderrdata.decode("utf-8"), end="")

        if process.returncode == 0:
            return True

        return False

    def get_packages_path(self):
        return sublime.packages_path()
        #return "d:/" # for testing purpose only

    def git_command(self, args, cwd):
        self.run_process(['git ' + args], cwd)

    def clone(self):
        sublime.status_message("Cloning...")
        self.git_command("clone " + self.get_credentials_repository_url() + " User", self.get_packages_path())
        sublime.status_message("Cloning...DONE")

    def forceClone(self):
        try:
            shutil.rmtree(self.get_packages_path() + os.sep + 'User');
        except FileNotFoundError:
            pass

        self.clone()

    def pull(self):
        sublime.status_message("Pulling...")
        self.git_command(["pull"], self.get_packages_path())
        sublime.status_message("Pulling...DONE")

    def commit(self):
        sublime.status_message("Commiting and pushing...")
        self.git_command("add *", "d:/SublimeSettings")
        self.git_command("commit -m update", "d:/SublimeSettings")
        self.git_command("push", "d:/SublimeSettings")
        sublime.status_message("Commiting and pushing...DONE")


    def run(self):
        user_packages_path = self.get_packages_path()
        print("Will sync: " + user_packages_path)
        #self.first_run()

        sublime.set_timeout_async(self.forceClone, 0)
        #sublime.set_timeout_async(self.pull, 0)
        #sublime.set_timeout_async(self.pull, 0)

        # #shutil.copytree(user_packages_path, "D:\\temp")
        # if not isGitInstalled():
        #     sublime.message_dialog("Git is not installed!")
        #     return
        # sublime.message_dialog("Git is installed!")
