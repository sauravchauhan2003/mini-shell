import os
import sys
from run_child import run_child
import shlex


def parseInput(arr):
    args, infile, outfile, append = [], None, None, False
    i = 0
    while i < len(arr):
        tok = arr[i]
        if tok in ("<", ">", ">>"):
            if i + 1 >= len(arr):
                return None
            name = arr[i + 1]
            if tok == "<":
                infile = name
            else:
                outfile = name
                append = (tok == ">>")
            i += 2
        else:
            args.append(tok)
            i += 1
    return args, infile, outfile, append





curr_dir=os.getcwd()
prev_dir=None
while True:
    try:
        command = input(curr_dir + "> ")
    except EOFError:
        print()
        sys.exit(0)
    except KeyboardInterrupt:
        print()
        continue
    try:
        arr = shlex.split(command)
    except ValueError as e:
        print(f"syntax error: {e}")
        continue
    if not arr:
        continue
    if arr[0]=="exit":
        sys.exit()
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
                    curr_dir=os.getcwd()
                except FileNotFoundError:
                    print(f"cd: {path}: No such file or directory")
                except NotADirectoryError:
                    print(f"cd: {path}: Not a directory")
                except PermissionError:
                    print(f"cd: {path}: Permission denied")
                except OSError as e:
                    print(f"cd: {path}: {e}")
    else:
        result = parseInput(arr)
        if result is None:
            print("syntax error: missing filename after redirection")
            continue
        args, infile, outfile, append = result
        if not args:
            print("syntax error: missing command")
            continue
        sys.stdout.flush()
        status = run_child(args, infile, outfile, append)




    