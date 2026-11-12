import os
import sys
curr_dir=os.getcwd()
prev_dir=None
while True:
    print(curr_dir+">")
    command=str(input())
    if(command=="exit"):
        sys.exit()
    if command=="":
        continue
    arr=command.split()
    if arr[0]=="cd":
        if(len(arr)!=2):
            print("Incorrect cd command")
            continue
        else:
            if arr[1]==".":
                continue
            elif arr[1]=="..":
                new_curr=os.path.dirname(curr_dir)
                prev_dir=curr_dir
                os.chdir(new_curr)
                curr_dir=new_curr
            elif arr[1]=='-':
                if prev_dir is None:
                    print("No last working directory")
                else:
                    os.chdir(prev_dir)
                    prev_dir,curr_dir=curr_dir,prev_dir    
            else:
                try:
                    path=arr[1]
                    os.chdir(path)
                    prev_dir=curr_dir
                    curr_dir=path
                except FileNotFoundError:
                    print(f"cd: {path}: No such file or directory")
                except NotADirectoryError:
                    print(f"cd: {path}: Not a directory")
                except PermissionError:
                    print(f"cd: {path}: Permission denied")
                except OSError as e:
                    print(f"cd: {path}: {e}")


    