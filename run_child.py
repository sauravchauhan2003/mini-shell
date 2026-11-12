import os
import sys

def run_child(arr, infile=None, outfile=None, append=False):
    pid = os.fork()

    if pid == 0:
        try:
            if infile is not None:
                fd = os.open(infile, os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)

            if outfile is not None:
                flags = os.O_WRONLY | os.O_CREAT
                flags |= os.O_APPEND if append else os.O_TRUNC

                fd = os.open(outfile, flags, 0o644)
                os.dup2(fd, 1)
                os.close(fd)

            os.execvp(arr[0], arr)

        except PermissionError:
            print(
                "Permission error: You do not have permission to execute that command",
                file=sys.stderr,
                flush=True
            )
        except OSError as e:
            print(f"{arr[0]}: {e}", file=sys.stderr, flush=True)

        os._exit(127)

    else:
        _, status = os.waitpid(pid, 0)

        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)

        elif os.WIFSIGNALED(status):
            return 128 + os.WTERMSIG(status)