import os
import sys

def spawn(args, infile=None, outfile=None, append=False,stdin_fd=None, stdout_fd=None, close_fds=()):
    sys.stdout.flush()
    pid = os.fork()
    if pid != 0:
        return pid                      # parent: just hand back the pid

    try:
        # 1. pipe wiring
        if stdin_fd is not None:
            os.dup2(stdin_fd, 0)
        if stdout_fd is not None:
            os.dup2(stdout_fd, 1)
        for fd in close_fds:            # every pipe end, after the dup2s
            os.close(fd)

        # 2. file redirections (these override the pipe if both are given)
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
        except OSError as e:
            name = e.filename or "redirection"
            print(f"shell: {name}: {e.strerror}", file=sys.stderr, flush=True)
            os._exit(1)

        # 3. exec
        try:
            os.execvp(args[0], args)
        except PermissionError:
            print(f"{args[0]}: permission denied", file=sys.stderr, flush=True)
            os._exit(126)
        except OSError as e:
            print(f"{args[0]}: {e.strerror}", file=sys.stderr, flush=True)
            os._exit(127)
    finally:
        os._exit(127)                   # the child can never return to the shell loop