
import os
import shutil
import subprocess
import datetime
import logging
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directories
original_dir = os.path.expanduser("~/backups/original")
tool_versions_file = "dot-files/.tool-versions"
dest_tool_versions_file = os.path.expanduser("~/.tool-versions")
plugins_file = "asdf-plugins.txt"

# Ensure original directory exists
os.makedirs(original_dir, exist_ok=True)

def backup_and_sync(source: str, dest: str, backup: str) -> None:
    if os.path.exists(dest):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dest = os.path.join(backup, f"{os.path.basename(dest)}-{timestamp}")
        logging.info(f"Moving existing {dest} to {backup_dest}")
        shutil.move(dest, backup_dest)

    logging.info(f"Syncing {source} with {dest}")
    shutil.copy(source, dest)

# Backup and sync .tool-versions file
backup_and_sync(tool_versions_file, dest_tool_versions_file, original_dir)

# Custom plugins with URLs
custom_plugins = ["cowsay", "mypy"]
custom_url = "https://github.com/amrox/asdf-pyapp.git"

def run_command(command: str) -> bool:
    logging.info(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for stdout_line in iter(process.stdout.readline, ""):
        logging.info(stdout_line.strip())
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        for stderr_line in iter(process.stderr.readline, ""):
            logging.error(stderr_line.strip())
        process.stderr.close()
        return False
    return True

def get_plugins_to_install() -> Dict[str, List[str]]:
    if os.path.exists(plugins_file):
        with open(plugins_file, "r") as f:
            plugins = f.read().splitlines()
        
        # Get current plugins
        current_plugins = subprocess.run("asdf plugin list", shell=True, capture_output=True, text=True).stdout.splitlines()
        
        plugins_to_install = {
            "default": [],
            "custom": []
        }
        
        for plugin in plugins:
            if plugin:
                if plugin not in current_plugins:
                    if plugin in custom_plugins:
                        plugins_to_install["custom"].append(plugin)
                    else:
                        plugins_to_install["default"].append(plugin)
                else:
                    logging.info(f"asdf plugin {plugin} is already installed")
        
        return plugins_to_install
    else:
        logging.error(f"Error: {plugins_file} not found")
        exit(1)

def install_plugins(plugins_to_install: Dict[str, List[str]]) -> None:
    for plugin in plugins_to_install["custom"]:
        command = f"asdf plugin add {plugin} {custom_url}"
        logging.info(f"Installing custom asdf plugin: {plugin}")
        if not run_command(command):
            logging.error(f"Failed to install custom plugin: {plugin}")
    
    for plugin in plugins_to_install["default"]:
        command = f"asdf plugin add {plugin}"
        logging.info(f"Installing asdf plugin: {plugin}")
        if not run_command(command):
            logging.error(f"Failed to install plugin: {plugin}")

def install_versions() -> None:
    installed_versions = {}
    
    if os.path.exists(dest_tool_versions_file):
        with open(dest_tool_versions_file, "r") as f:
            lines = f.read().splitlines()
        
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                try:
                    plugin, version = line.split()
                    installed_versions[plugin] = version
                except ValueError:
                    logging.error(f"Malformed line in .tool-versions file: {line}")
    
    with open(plugins_file, "r") as f:
        plugins = f.read().splitlines()

    for plugin in plugins:
        if plugin:
            if plugin in installed_versions:
                logging.info(f"Installing {plugin} version {installed_versions[plugin]}")
                if not run_command(f"asdf install {plugin} {installed_versions[plugin]}"):
                    logging.error(f"Failed to install {plugin} {installed_versions[plugin]}")
                if not run_command(f"asdf global {plugin} {installed_versions[plugin]}"):
                    logging.error(f"Failed to set global version for {plugin} {installed_versions[plugin]}")
            else:
                logging.info(f"No version specified for {plugin}. Installing latest version.")
                if not run_command(f"asdf install {plugin} latest"):
                    logging.error(f"Failed to install latest version for {plugin}")
                if not run_command(f"asdf global {plugin} latest"):
                    logging.error(f"Failed to set global version for {plugin} to latest")

def main() -> None:
    plugins_to_install = get_plugins_to_install()
    install_plugins(plugins_to_install)
    install_versions()
    logging.info("Setup complete!")

if __name__ == "__main__":
    main()



# import os
# import shutil
# import subprocess
# import datetime
# import logging
# from typing import Dict, List

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Directories
# original_dir = os.path.expanduser("~/backups/original")
# tool_versions_file = "dot-files/.tool-versions"
# dest_tool_versions_file = os.path.expanduser("~/.tool-versions")
# plugins_file = "asdf-plugins.txt"

# # Ensure original directory exists
# os.makedirs(original_dir, exist_ok=True)

# def backup_and_sync(source: str, dest: str, backup: str) -> None:
#     if os.path.exists(dest):
#         timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#         backup_dest = os.path.join(backup, f"{os.path.basename(dest)}-{timestamp}")
#         logging.info(f"Moving existing {dest} to {backup_dest}")
#         shutil.move(dest, backup_dest)

#     logging.info(f"Syncing {source} with {dest}")
#     shutil.copy(source, dest)

# # Backup and sync .tool-versions file
# backup_and_sync(tool_versions_file, dest_tool_versions_file, original_dir)

# # Custom plugins with URLs
# custom_plugins = ["cowsay", "mypy"]
# custom_url = "https://github.com/amrox/asdf-pyapp.git"

# def run_command(command: str) -> bool:
#     logging.info(f"Running command: {command}")
#     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     for stdout_line in iter(process.stdout.readline, ""):
#         logging.info(stdout_line.strip())
#     process.stdout.close()
#     return_code = process.wait()
#     if return_code != 0:
#         for stderr_line in iter(process.stderr.readline, ""):
#             logging.error(stderr_line.strip())
#         process.stderr.close()
#         return False
#     return True

# def get_plugins_to_install() -> Dict[str, List[str]]:
#     if os.path.exists(plugins_file):
#         with open(plugins_file, "r") as f:
#             plugins = f.read().splitlines()
#         
#         # Get current plugins
#         current_plugins = subprocess.run("asdf plugin list", shell=True, capture_output=True, text=True).stdout.splitlines()
#         
#         plugins_to_install = {
#             "default": [],
#             "custom": []
#         }
#         
#         for plugin in plugins:
#             if plugin:
#                 if plugin not in current_plugins:
#                     if plugin in custom_plugins:
#                         plugins_to_install["custom"].append(plugin)
#                     else:
#                         plugins_to_install["default"].append(plugin)
#                 else:
#                     logging.info(f"asdf plugin {plugin} is already installed")
#         
#         return plugins_to_install
#     else:
#         logging.error(f"Error: {plugins_file} not found")
#         exit(1)

# def install_plugins(plugins_to_install: Dict[str, List[str]]) -> None:
#     for plugin in plugins_to_install["custom"]:
#         command = f"asdf plugin add {plugin} {custom_url}"
#         logging.info(f"Installing custom asdf plugin: {plugin}")
#         if not run_command(command):
#             logging.error(f"Failed to install custom plugin: {plugin}")
#     
#     for plugin in plugins_to_install["default"]:
#         command = f"asdf plugin add {plugin}"
#         logging.info(f"Installing asdf plugin: {plugin}")
#         if not run_command(command):
#             logging.error(f"Failed to install plugin: {plugin}")

# def install_versions() -> None:
#     if os.path.exists(dest_tool_versions_file):
#         with open(dest_tool_versions_file, "r") as f:
#             lines = f.read().splitlines()
#         
#         for line in lines:
#             if line.strip() and not line.strip().startswith("#"):
#                 try:
#                     plugin, version = line.split()
#                     logging.info(f"Installing {plugin} version {version}")
#                     if not run_command(f"asdf install {plugin} {version}"):
#                         logging.error(f"Failed to install {plugin} {version}")
#                     if not run_command(f"asdf global {plugin} {version}"):
#                         logging.error(f"Failed to set global version for {plugin} {version}")
#                 except ValueError:
#                     logging.error(f"Malformed line in .tool-versions file: {line}")
#     else:
#         logging.error(f"Error: {dest_tool_versions_file} not found")
#         exit(1)

# def main() -> None:
#     plugins_to_install = get_plugins_to_install()
#     install_plugins(plugins_to_install)
#     install_versions()
#     logging.info("Setup complete!")

# if __name__ == "__main__":
#     main()

