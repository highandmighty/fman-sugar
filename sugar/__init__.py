from fman import DirectoryPaneCommand, show_status_message, show_alert
from fman.url import as_url, as_human_readable, splitscheme
from fman.fs import move
from fman.clipboard import set_text
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
        if dir_key in dirs and os.path.exists(dirs[dir_key]):
            self.pane.set_path(as_url(dirs[dir_key]))
            show_status_message("Favourite directory #{} is here.".format(dir_key), 3)
        else:
            show_alert("Favourite directory #{} is not set or not found.    ".format(dir_key))

# Open Favourites.json
class SetFavourites(DirectoryPaneCommand):
    def __call__(self):
        self.pane.run_command('open_file', args={"url": as_url(os.path.join(folder, 'Favourites.json'))})

# Show list of favourites
class ShowFavourites(DirectoryPaneCommand):
    def __call__(self):
        dirs_string = re.sub("[{}\']", "", str(dirs))
        show_alert(re.sub(",\s", "    \n", dirs_string + "    "))

class ShowSettings(DirectoryPaneCommand):
    def __call__(self):
        settings = os.path.join(os.path.dirname(folder), 'Settings')
        self.pane.set_path(as_url(settings))

class CopySafePathsToClipboard(DirectoryPaneCommand):
    def __call__(self):
        selected_file = self.pane.get_file_under_cursor()
        if selected_file:
            path = splitscheme(selected_file)[1]
            set_text(path)
            show_status_message('Copied {} to the clipboard'.format(path), 5)

# Unzip file to same folder
class UnzipFile(DirectoryPaneCommand):
    # Based on: https://github.com/thomas-haslwanter/fman_unzip
    def __call__(self):
        selected_file = self.pane.get_file_under_cursor()
        if not selected_file: # Empty dir
            show_alert("No files selected    ")
            return
        if not selected_file.endswith(('.zip')):
            show_alert("This is not a zip-archive!    ")
            return

        dirPath = os.path.dirname(as_human_readable(selected_file))
        unZipName = os.path.basename(as_human_readable(selected_file))
        unZipDir = unZipName[:-4]
        unZipPath = os.path.join(dirPath, unZipDir)

        if os.path.isdir(unZipPath):
            show_alert("Target directory already exists    ")
            return

        zipfile.ZipFile(as_human_readable(selected_file)).extractall(path=unZipPath)
        self.pane.reload()
        show_status_message("Files were unzipped to directory {0}".format(unZipDir), 5)

# Show the same in right pane
class SamePaneRight(DirectoryPaneCommand):
    # Based on: https://github.com/raguay/SwapPanels
    def __call__(self):
        panes = self.pane.window.get_panes()
        left_pane = panes[0]
        right_pane = panes[1]
        right_pane.set_path(left_pane.get_path())
        right_pane.focus()

class SwapPanes(DirectoryPaneCommand):
    # Based on: https://github.com/raguay/SwapPanels
    def __call__(self):
        panes = self.pane.window.get_panes()
        left_pane = panes[0]
        right_pane = panes[1]
        right_pane_path = right_pane.get_path()

        right_pane.set_path(left_pane.get_path())
        left_pane.set_path(right_pane_path)

# Open directory in Command Prompt
class TerminalHere(DirectoryPaneCommand):
    def __call__(self):
        selected_folder = as_human_readable(self.get_chosen_files()[0])

        if os.path.isfile(selected_folder):
            selected_folder = os.path.dirname(selected_folder)

        if os.path.isdir(selected_folder):
            subprocess.call("start /D \"{}\" cmd".format(selected_folder), shell=True)
        else:
            show_alert("Can not start Command Prompt here    ")

# Open directory in Command Prompt
class Archive(DirectoryPaneCommand):
    def __call__(self):
        file_under_cursor = self.pane.get_file_under_cursor()
        if not file_under_cursor:
            return # Empty dir

        file_dir = os.path.dirname(as_human_readable(file_under_cursor))
        file_name = os.path.basename(as_human_readable(file_under_cursor))
        new_path = os.path.join(file_dir, '-' + file_name)

        if os.path.exists(new_path):
            show_alert('{} already exists!    '.format('-' + file_name))
            return

        move(file_under_cursor, as_url(new_path))
        self.pane.reload()
        self.pane.place_cursor_at(as_url(new_path))
