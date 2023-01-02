import json
import os
from collections import defaultdict
from pathlib import Path

import git


class GitCTX:
    def __init__(self):
        self.__gitctx_folder = (Path().home() / ".gitctx").absolute()
        self.__config_path = self.__gitctx_folder / "config"
        self.__context_path = self.__gitctx_folder / "context"
        self.__check_gitctx_folder()
        self.__init_gitctx_context()

    def create(self, *, context_name, user_name, user_email):
        gitctx_config = self.__load_gitctx_config()
        if context_name in gitctx_config["contexts"]:
            raise Exception  # already exists exception
        gitctx_config["contexts"][context_name] = {
            "user_name": user_name,
            "user_email": user_email,
        }
        self.__save_gitctx_config(gitctx_config=gitctx_config)

    def use(self, *, context_name) -> dict:
        gitctx_config = self.__load_gitctx_config()
        if context_name not in gitctx_config["contexts"]:
            raise Exception  # not found
        gitctx_config["active_context"] = context_name
        gitctx_context = git.config.GitConfigParser(file_or_files=self.__context_path, read_only=False)
        gitctx_context.remove_section(section="user")
        for key, values in gitctx_config["contexts"][context_name].items():
            for value in values:
                gitctx_context.add_value(section="user", option=key, value=value)
        gitctx_context.write()
        self.__save_gitctx_config(gitctx_config=gitctx_config)
        return gitctx_config

    def update(self, *, context_name, user_name, user_email):
        gitctx_config = self.__load_gitctx_config()
        if context_name not in gitctx_config["contexts"]:
            raise Exception  # not found
        gitctx_config["contexts"][context_name] = {
            "user_name": user_name,
            "user_email": user_email,
        }
        self.__save_gitctx_config(gitctx_config=gitctx_config)

    def delete(self, *, context_name):
        if context_name == "default":
            raise Exception()  # cannot delete default context
        gitctx_config = self.__load_gitctx_config()
        if gitctx_config["active_context"] == context_name:
            gitctx_config = self.use(context_name="default")
        del gitctx_config["contexts"][context_name]
        self.__save_gitctx_config(gitctx_config=gitctx_config)

    def show(self, *, fields: list[str]):
        gitctx_config = self.__load_gitctx_config()
        active_context = gitctx_config["active_context"]
        print(active_context)

    def list(self):
        gitctx_config = self.__load_gitctx_config()
        for context in gitctx_config["contexts"]:
            print(context)

    def __check_gitctx_folder(self):
        if not self.__gitctx_folder.exists():
            os.mkdir(self.__gitctx_folder)

    def __init_gitctx_config(self, *, user: dict = None):
        if not self.__config_path.exists():
            self.__config_path.touch(mode=0o644, exist_ok=True)
            self.__save_gitctx_config(gitctx_config={})
        if user:
            gitctx_config = self.__load_gitctx_config()
            gitctx_config["active_context"] = "default"
            gitctx_config["contexts"]["default"] = user
            json.dump(obj=gitctx_config, fp=self.__config_path.open(mode="w+"))

    def __init_gitctx_context(self):
        gitconfig = git.config.GitConfigParser(file_or_files=git.config.get_config_path("global"), read_only=False, merge_includes=False)

        gitconfig.read()
        user = dict()
        if gitconfig.has_section("user"):
            user = {item[0]: item[1] for item in gitconfig.items_all(section_name="user")}
            gitconfig.remove_section(section="user")

        if not gitconfig.has_option(section="include", option="path") or str(self.__context_path) not in gitconfig.get_values(section="include", option="path"):
            gitconfig.add_value(section="include", option="path", value=str(self.__context_path))

        self.__context_path.touch(mode=0o644, exist_ok=True)
        gitctx_context = git.config.GitConfigParser(file_or_files=self.__context_path, read_only=False)
        for key, values in user.items():
            for value in values:
                gitctx_context.add_value(section="user", option=key, value=value)

        gitconfig.write()
        gitctx_context.write()
        self.__init_gitctx_config(user=user)

    def __load_gitctx_config(self) -> defaultdict:
        with self.__config_path.open(mode="r") as file:
            configuration = json.load(fp=file)
            return defaultdict(dict, configuration)

    def __save_gitctx_config(self, *, gitctx_config: defaultdict):
        with self.__config_path.open(mode="w+") as file:
            json.dump(obj=gitctx_config, fp=file)
