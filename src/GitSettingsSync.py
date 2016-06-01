import sublime
import sublime_plugin
import os
import shutil
import subprocess

# PUT SCRIPT IN Application Data\Sublime Text 3\Packages

def isGitInstalled():
        try:
            out = subprocess.check_output(["git", "--version"])
            return True
        except subprocess.CalledProcessError as e:
            return False

class SyncCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        user_packages_path = sublime.packages_path() + os.sep + 'User'
        print("Will sync: " + user_packages_path)
        #shutil.copytree(user_packages_path, "D:\\temp")
        if not isGitInstalled():
            sublime.message_dialog("Git is not installed!")
            return
        sublime.message_dialog("Git is installed!")
