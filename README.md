# GitCTX - A kubectx-like tool for Git
NOTE: this project is a work in progress and in early stages of development. It
should in no way be considered production ready.

## Usage
Available commands:
```shell
gitctx  # Shows the help message
gitctx create <context_name> --user-name=<user.name> --user-email=<user.email>  # creates a new gitcontext using the given parameters
gitctx delete <context_name>  # deletes the given gitcontext
gitctx list  # list all available gitcontexts
gitctx show  # show the currently active gitcontext
gitctx update <context_name> --user-name=<user.name> --user-email=<user.email>  # updates the gitcontext using the given parameters
gitctx use <context_name>  # switches the active gitcontext
```