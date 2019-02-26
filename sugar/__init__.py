from fman import DirectoryPaneCommand, show_status_message, show_alert
from fman.url import as_url, as_human_readable
import os
import json
import re
import zipfile
import subprocess

plugin = os.path.dirname(os.path.realpath(__file__))
folder = os.path.dirname(plugin)
os.chdir(folder)

with open('Favourites.json', encoding='utf-8') as json_file:
    dirs = json.load(json_file)

# Go to favourite folder
class GoToFavourite(DirectoryPaneCommand):
    def __call__(self, dir_num=1):
        dir_key = str(dir_num)
        if dir_key in dirs:
            self.pane.set_path(as_url(dirs[dir_key]))
            show_status_message("Favourite directory #{} is here.".format(dir_key), 3)
        else:
            show_alert("Favourite directory #{} is not set.    ".format(dir_key))

# Open Favourites.json
class SetFavourites(DirectoryPaneCommand):
    def __call__(self):
        self.pane.run_command('open_file', args={"url": as_url(os.path.join(folder, 'Favourites.json'))})

# Show list of favourites
class ShowFavourites(DirectoryPaneCommand):
    def __call__(self):
        dirs_string = re.sub("[{}\']", "", str(dirs))
        show_alert(re.sub(",\s", "    \n", dirs_string + "    "))

# Unzip file to same folder
class UnzipFile(DirectoryPaneCommand):
    # Based on: https://github.com/thomas-haslwanter/fman_unzip
    def __call__(self):
        selected_files = self.get_chosen_files()
        if len(selected_files) == 0:
            show_alert("No files selected    ")
            return
        elif len(selected_files) > 1:
            show_alert("More than one file selected    ")
            return

        dirPath = os.path.dirname(as_human_readable(selected_files[0]))
        unZipName = os.path.basename(as_human_readable(selected_files[0]))
        inFile = os.path.join(dirPath, unZipName)
        if not inFile.endswith(('.zip')):
            show_alert("This is not a zip-archive!    ")
            return

        unZipDir = unZipName[:-4]
        unZipPath = os.path.join(dirPath, unZipDir)
        if os.path.isdir(unZipPath):
            show_alert("Target directory already exists    ")
            return

        zipfile.ZipFile(inFile).extractall(path=unZipPath)
        self.pane.reload()
        show_status_message("Files were unzipped to directory {0}".format(unZipDir), 5)

# Show the same in right pane
class SamePanelRight(DirectoryPaneCommand):
    # Based on: https://github.com/raguay/SwapPanels
    def __call__(self):
        panes = self.pane.window.get_panes()
        left_pane = panes[0]
        left_pane_path = left_pane.get_path()
        right_pane = panes[1]
        right_pane.set_path(left_pane_path)

# Open directory in Command Prompt
class CommandPromptHere(DirectoryPaneCommand):
    def __call__(self):
        selected_folder = as_human_readable(self.get_chosen_files()[0])

        if os.path.isfile(selected_folder):
            selected_folder = os.path.dirname(selected_folder)

        if os.path.isdir(selected_folder):
            subprocess.call("start /D \"{}\" cmd".format(selected_folder), shell=True)
        else:
            show_alert("Can not start Command Prompt here    ")
