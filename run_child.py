import os
def run_child(arr):
    pid=os.fork()
    if(pid==0):
        try:
            os.execvp(arr[0],arr)
        except OSError:
            print(f"{arr[0]}: command not found", flush=True)
        os._exit(127)
    else:
        _, status = os.waitpid(pid, 0)
        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
            print("Exit code:", exit_code)

        elif os.WIFSIGNALED(status):
            signal_num = os.WTERMSIG(status)
            print("Terminated by signal:", signal_num)