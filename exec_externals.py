import subprocess


class ExternalCommandError(Exception):
    pass


class ExternalCommandWrapper:
    """A simple wrapper for executing all kinds of external commands, e.g., ls"""
    def __init__(self, cmd, cmd_args=None, shell=False, verbose=False):
        if cmd_args is None:
            cmd_args = []
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.shell = shell
        self.verbose = verbose

    def run(self):
        """Run the command"""
        full_cmd = [self.cmd]
        if len(self.cmd_args) > 0:
            full_cmd += self.cmd_args
        try:
            if self.verbose:
                print("Running `{command}`".format(command=" ".join(full_cmd)))
            p = subprocess.Popen(full_cmd,
                                 shell=self.shell,
                                 stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            p.wait()
            p.stdout.close()
        except OSError as e:
            raise ExternalCommandError("Failed to execute command: " + str(e)) from e

