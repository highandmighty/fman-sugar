from fman import DirectoryPaneCommand, show_status_message, clear_status_message, show_alert, YES, NO
from fman.url import as_url, as_human_readable, splitscheme
from fman.fs import move
from fman.clipboard import set_text
import os
import json
import re
import zipfile
import subprocess
from sys import platform
import tempfile
import shutil
import hashlib

plugin = os.path.dirname(os.path.realpath(__file__))
folder = os.path.dirname(plugin)
os.chdir(folder)

# Favourites settings
with open('Favourites.json', encoding='utf-8') as json_file:
    dirs = json.load(json_file)

# Unarchiving tools settings
try:
    with open('Tools.json', encoding='utf-8') as json_file:
        tools = json.load(json_file)
except:
    tools = {}

# Go to favourite folder
class GoToFavourite(DirectoryPaneCommand):
    def __call__(self, dir_num=1):
        dir_key = str(dir_num)
        if dir_key in dirs and os.path.exists(dirs[dir_key]):
            self.pane.set_path(as_url(dirs[dir_key]))
            self.pane.reload()
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
    def __call__(self, tools=tools):
        # Loading custom unarchiving tools
        if not tools:
            tools_path = os.path.abspath('Tools.json')
            show_alert(f"Tools.json file not found in:\n{tools_path}")
            return

        selected_file = self.pane.get_file_under_cursor()
        zip_path = as_human_readable(selected_file)
        if not selected_file:
            show_alert("No files selected    ")
            return

        if not selected_file.endswith(('.gz', '.bz2', '.rar', '.zip', '.7z')):
            show_alert("This is not a valip zip-archive!    ")
            return

        parent = os.path.dirname(zip_path)
        tmp_dir = os.path.realpath(tempfile.gettempdir())

        zip_name = os.path.basename(zip_path)
        zip_dirname = os.path.splitext(zip_name)[0]
        zip_dir = os.path.join(parent, zip_dirname)
        tmp_zip_dir = os.path.join(tmp_dir, zip_dirname)

        if os.path.isdir(zip_dir):
            show_alert("Target directory already exists    ")
            return

        if 'unar' in tools:
            show_status_message("Unarchiving files with 'unar' utility...")

            command = [tools['unar'], '-o', tmp_dir, '-d', '-q', zip_path]
            #show_alert(f"{' '.join(command)}")
            s = subprocess.run(command, shell=False)

            if s.returncode != 0:
                show_alert("Unable to unarchive file    ")
                shutil.rmtree(tmp_zip_dir)
                clear_status_message()
                return

            shutil.move(tmp_zip_dir, zip_dir)
        else:
            show_alert("'zipfile' is used for unarchiving\ntools file: '{}'".format(str(tools)))
            # TO DO: default method can only work with .zip-file
            # TO DO: default method output dir is sometimes wrong
            #show_status_message("Unarchiving files with default utility...")
            #zipfile.ZipFile(zip_path).extractall(path=zip_dirname)

        self.pane.reload()
        clear_status_message()
        show_alert(f"Files were unzipped to directory '{zip_dirname}'")

# Open directory in Command Prompt
class ZipFile(DirectoryPaneCommand):
    def __call__(self):
        # self.pane.get_selected_files() may be added in future
        object_under_cursor = as_human_readable(self.pane.get_file_under_cursor())
        os.chdir(os.path.dirname(object_under_cursor))
        object_relative = os.path.relpath(object_under_cursor)

        if not object_relative:
            return # Empty dir

        # Computing archive filename
        if os.path.isfile(object_relative):
            # File
            if object_relative.endswith('.zip'):
                show_status_message("File is already zipped!", 5)
                return
            zipname = os.path.splitext(object_relative)[0] + '.zip'
        else:
            # Directory
            zipname = object_relative + '.zip'

        if os.path.exists(zipname):
            a = show_alert('{} already exists!\nRewrite the old one?    '.format(zipname), YES | NO, NO)
            if a == NO:
                return

        # Creating zip-archive in temp dir
        show_status_message('Zipping in progress...')
        tmpdir = tempfile.gettempdir()
        # TO DO: tmp_dir = os.path.realpath(tmp_dir) # .gettempdir() may return symlink on MacOS
        tmpname = os.path.join(tmpdir, zipname)

        with zipfile.ZipFile(tmpname, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(object_relative):
                os.chdir(object_relative) # to exclude root folder from .zip
                for root, dirs, files in os.walk(object_under_cursor):
                    for file in files:
                        if not file.startswith("._") and not file == ".DS_Store":
                            zf.write(os.path.relpath(os.path.join(root, file)))
                os.chdir(os.path.dirname(object_under_cursor))
            else:
                zf.write(object_relative)

        # Moving archive to current dir
        move(as_url(tmpname), as_url(os.path.abspath(zipname)))

        self.pane.reload()
        clear_status_message()
        show_alert('{} is created!    '.format(zipname))
        #self.pane.place_cursor_at(as_url(os.path.abspath(zipname))) # Raises Error

# Show the same in right pane
class SamePane(DirectoryPaneCommand):
    # Based on: https://github.com/raguay/SwapPanels
    def __call__(self, direction='right'):
        panes = self.pane.window.get_panes()
        if direction == 'right':
            from_pane, to_pane = panes[0], panes[1]
        else:
            from_pane, to_pane = panes[1], panes[0]

        if to_pane == self.pane:
            show_status_message("Choose the opposite pane, not the same one!", 5)
            return
        to_pane.set_path(from_pane.get_path())
        to_pane.focus()

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
            if platform == "darwin":
                show_alert('open -a Terminal \'{}\''.format(selected_folder))
                subprocess.call('open -a Terminal \'{}\''.format(selected_folder), shell=True)
            elif platform == "win32":
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

# Two files comparison
# MD5 Checksum
def checksum(filename, blocksize=4096):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash_md5.update(block)
    return hash_md5.hexdigest()

class ChecksumFiles(DirectoryPaneCommand):
    def __call__(self):
        panes = self.pane.window.get_panes()
        selected = panes[0].get_selected_files()
        selected.extend(panes[1].get_selected_files())

        if len(selected) not in (1, 2):
            show_alert("Choose exactly two files for comparison    ")
            return

        show_status_message("Calculating checksums for files...", 5)
        checksums = []
        for file in selected:
            path = as_human_readable(file)
            if os.path.isfile(path):
                checksums.append(checksum(path))
            else:
                show_alert("Only files are comparable    ")
                return

        if len(checksums) == 1:
            show_alert("File's checksum is:\n{}    ".format(checksums[0]))
        elif checksums[0] == checksums[1]:
            show_alert("Files are exactly the same:\n{}\n{}    ".format(checksums[0], checksums[1]))
        else:
            show_alert("Files are different:\n{}\n{}    ".format(checksums[0], checksums[1]))
