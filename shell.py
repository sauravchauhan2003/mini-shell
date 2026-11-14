import os
import sys
from run_child import spawn
import shlex
import signal
def pipecommand(arr):
    n = len(arr)
    l = []
    for x in arr:
        curr = list(x)
        curr += [None, None, None]      # stdin_fd, stdout_fd, close_fds
        l.append(curr)
    all_fds = []
    i = 0
    while i < n - 1:
        r, w = os.pipe()
        l[i][5] = w                     # command i writes into the pipe
        l[i + 1][4] = r                 # command i+1 reads from it
        all_fds.extend((r, w))
        i += 1
    for k in range(n):
        l[k][6] = all_fds               # every child closes every pipe fd
        l[k] = tuple(l[k])
    return l, all_fds
    
    


def split_pipeline(arr):
    ans=[]
    curr=[]
    for x in arr:
        if x=='|':
            if len(curr)==0:
                return None
            ans.append(curr)
            curr=[]
        else:
            curr.append(x)
    if len(curr)==0:
        return None
    ans.append(curr)
    return ans;



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
        lex = shlex.shlex(command, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        arr = list(lex)
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
        segments=split_pipeline(arr)
        if segments is None:
            print("Syntax error:Wrong use of pipe operator")
            continue
        jobs=[]
        for segment in segments:
            curr=parseInput(segment)
            if curr is None:
                jobs=None
                break
            args, infile, outfile, append=curr
            if not args:
                jobs=None
                break
            jobs.append(curr)
        if jobs is None:
            print("Syntax error in command")
            continue
        sys.stdout.flush()
        specs, all_fds = pipecommand(jobs)
        pids = []
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        for args, infile, outfile, append, stdin_fd, stdout_fd, close_fds in specs:
            pids.append(spawn(args, infile, outfile, append, stdin_fd, stdout_fd, close_fds))

        for fd in all_fds:                      # the shell closes its copies too
            os.close(fd)

        last_status = None
        for pid in pids:
            _, status = os.waitpid(pid, 0)
            if pid == pids[-1]:
                last_status = status
        signal.signal(signal.SIGINT, signal.default_int_handler)