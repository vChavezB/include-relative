"""
	Copyright (C) 2022 Victor Chavez
	vchavezb@protonmail.com
    This file is part of Relative Include
	
    Relative Include is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    Relative Include is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Relative Include.  If not, see <https://www.gnu.org/licenses/>.
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import pathlib
import shutil
import re
import argparse
import os
import json
import collections.abc
import logging
from ._version import __version__

logger = logging.getLogger(__name__)

class Log:
    @staticmethod
    def init(level):
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%H:%M:%S')
        logger.setLevel(level)

class IncludeRegex:
    include_directive = '([ ]*#)([ ]*include)([ ]*["<])[^>\"]*[>\"]'
    include_path = '([.]*?<=["<])(.*?)(?=[">][.]*)'


class RelativeIncludeCfg:
    """
    The default JSON setup config to use this script
    """
    default = {
        'include_paths': [],
        "out":
        {
                "dir": "RelativeLib_Out",
                "overwrite": True
        },
        #Include path options
        "options":
        {
            "include_same_dir": True,
            "root_include": True
        },
        "lib_path": None,
        "debug": False,
        "silent": False
    }
    @staticmethod
    def update(d, u):
        """
        Update the JSON config keys
        """
        for (k, v) in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = RelativeIncludeCfg.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('config_file', default='', type=str,
                            help='JSON Config file to run this script')
        parser.add_argument('-s', dest='silent', action='store_true',
                            help='Silent output')
        parser.add_argument('-d', dest='debug', action='store_true',
                            help='Print debug messages')
        parser.add_argument('-V', '--version', action='version',
                            version=__version__)
        args = parser.parse_args()
        return vars(args)

    @staticmethod
    def parse_args(cmd_args):
        setup_config = RelativeIncludeCfg.default
        cfg_path = pathlib.Path(cmd_args['config_file']).absolute()
        error_msg = ''
        if not os.path.exists(cfg_path):
            raise Exception('Setup File %s does not exist!'
                            % cmd_args['config_file'])

        try:
            with open(cfg_path) as json_file:
                user_setup_data = json.load(json_file)
                user_setup_data.update({"args":cmd_args})
                setup_config = RelativeIncludeCfg.update(setup_config, user_setup_data)
        except:
            raise Exception('Config File could not be interpreted!')
        return setup_config

    @staticmethod
    def get_config():
        cmd_args = RelativeIncludeCfg.get_args()
        setup_config = RelativeIncludeCfg.parse_args(cmd_args)
        return setup_config

class RelativeInclude:
    file_ext = [".cpp", ".c", ".hpp", ".h"]

    def __init__(self, cfg):
        """
        Load the configuration settings
        and prepare the output directory
        :param cfg:
        """
        if cfg["silent"]:
            log_level = logging.ERROR
        elif cfg["debug"]:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        Log.init(log_level)
        self.config = cfg
        self.lib_path = pathlib.Path(cfg["lib_path"])
        self.out_dir = pathlib.Path(cfg["out"]["dir"])
        if not os.path.exists(self.lib_path):
            raise Exception('Library path "%s" does not exist!'
                            % self.lib_path)
        if os.path.exists(self.out_dir):
            if cfg["out"]["overwrite"]:
                shutil.rmtree(self.out_dir, ignore_errors=True)
            else:
                raise Exception("Output directory %s already exists, please delete it or set overwrite cfg to True" % (self.out_dir))

        shutil.copytree(self.lib_path.absolute(), self.out_dir.absolute())
        os.chdir(self.out_dir)
        self.includeDirective = re.compile(IncludeRegex.include_directive)
        self.includePath = re.compile(IncludeRegex.include_path)

    def __list_all_files(self, path):
        """
        List all files in a given path
        :param path: Path where to begin the recursive search
        :return: List with file paths
        """
        file_list = []
        for r, d, f in os.walk(path):
            for file in f:
                filePath = pathlib.Path(os.path.join(r, file))
                file_list.append(filePath)
        return file_list

    def _getIncludePath(self, line):
        """
        Get the include path in a C/C++
        include directive line
        :param line: Line that has an include directive
        :return:
        """
        r = re.search('["<](.*)[">]', line)
        if r is not None:
            path = r.group(1)
            return pathlib.Path(path)
        return None

    def _findBestMatch(self, include_file):
        """
        Find the absolut path that matches the given partial include file path
        from the configuration list of include directories of the user
        :param include_file: Partial include file path obtained from #include <Myfile.h> (e.g. MyFile.h)
        :return: The absolute path of the include_file, None if not found
        """
        for path in self.config["include_paths"]:
            inc_path = pathlib.Path(path)
            absolute_path = inc_path.joinpath(include_file)
            if absolute_path.exists():
                return absolute_path
        return None

    def _includeValid(self, fileDir, include_file):
        """
        Checks that an include directive is valid relative to the file
        which uses it
        :param fileDir:
        :param include_file:
        :return:
        """
        relative_path = fileDir.joinpath(include_file)
        if os.path.exists(relative_path):
            return True
        else:
            return False

    def _get_nesting_level(self, file_path):
        """
        Count how many directories below is a path with respect to its root
        :param file_path: File path that is nested in a root directory
        :return:
        """
        cnt = 0
        while file_path != pathlib.Path("."):
            file_path = file_path.parent
            cnt += 1
        return cnt

    def _build_relative_path(self, nesting_level, include_file_path):
        """
        Create a relative include directive path with the number of nesting levels
        :param nesting_level: how many levels above are you moving above
        :param include_file_path: 
        :return:
        """
        top_level = "../" * nesting_level
        file_path_str = str(include_file_path).replace('\\', '/')
        return '#include "%s"' % (top_level + str(file_path_str))

    def _count_relative_levels(self, include_path):
        """
        Count the number of relative levels used in an include directive
        e.g. "../../test.h" has 2 relative levels
        :param include_path: the path inside the include directive <> or ""
        :return:
        """
        return str(include_path).count("..")

    def _isIncludeFileRelative(self, ref_file, include_file):
        """
        Checks if a given include file is relative to the file
        that references it
        :param ref_file:
        :param include_file:
        :return: dictionary with the results of the search
                - relative: True if the include is relative
                - Type: down if the include in a subdir
                        up if the include is a dir above
                - level: how many directories above or down
                         is the include located
        """
        result = {"relative": False, "type": None, "level": 0}
        try:
            include_dir = include_file.parent
            ref_file.relative_to(include_dir)
            result["type"] = "up"
            result["relative"] = True
        except Exception as e:
            pass
        try:
            ref_file_dir = ref_file.parent
            include_dir.relative_to(ref_file_dir)
            result["type"] = "down"
            result["relative"] = True
        except Exception as e:
            pass
        return result

    def _removeRelativeInclude(self, file_dir, include_path):
        """
        Remove relative includes done with "../"
        :param include_path:
        :param file_dir: file that is using the include path
        :return:
        """
        dir_level = self._count_relative_levels(include_path)
        if dir_level != 0:
            for i in range(dir_level):
                root_dir_include = file_dir.parent
            include_file = str(include_path).split("..")[-1]  # obtain include path
            include_path = pathlib.Path(include_file)
        return include_path

    def _fixPaths(self, filepath):
        """
        Fixes the include paths and makes them relative
        to the source file path
        :param filepath:
        :return: new file as a string with relative modifications
                 returns None otherwise
        """
        file = open(filepath, 'r')
        file_dir = pathlib.Path(filepath).parent
        new_file = ""
        paths_found = 0
        logger.debug('Parsing %s' % filepath)
        for line in file.readlines():
            found_new_path = False
            match_res = self.includeDirective.match(line)
            if match_res is not None:
                include_file = self._getIncludePath(line)
                if not self._includeValid(file_dir, include_file):
                    include_file = self._removeRelativeInclude(file_dir, include_file)
                    best_match = self._findBestMatch(include_file)
                    if best_match is not None:
                        result = self._isIncludeFileRelative(filepath, best_match)
                        """"
                        If the include file is relative to the directory
                        either in a subdir or updir 
                        """
                        if result["relative"]:
                            if result["type"] == "up":
                                """
                                Count how many levels deep is the source file
                                that includes the header
                                @TODO: Is there a pythonic way to do this with pathlib?
                                """
                                search_dir = file_dir
                                cnt = 0
                                while search_dir != best_match.parent:
                                    cnt += 1
                                    search_dir = search_dir.parent
                                new_path = self._build_relative_path(cnt, include_file.name)
                            else:
                                """
                                If the include header is in a subdir,simply get the 
                                relative path from the source file that includes it
                                """
                                include_file_subdir = best_match.relative_to(file_dir)
                                root_of_lib = filepath.parent == pathlib.Path(".")
                                if not self.config["options"]["include_same_dir"] and not root_of_lib:
                                    """
                                    In case the included file is in the same directory of the file.
                                    Make the include path relative to one directory above. This 
                                    can resolve conflicts in case the build system passes an include flag
                                    ("-I") to the compiler, as the wrong include file could be reference.
                                    """
                                    includeInSameDir = include_file_subdir.parent == pathlib.Path(".")
                                    if includeInSameDir:
                                        folder_of_file = pathlib.Path(filepath.parents[0].name)
                                        new_path = self._build_relative_path(1, folder_of_file.joinpath(best_match.name))
                                else:
                                    new_path = self._build_relative_path(0, include_file_subdir)
                        else:
                            """
                            If the include file is not relative, set the include
                            file relative to the root of the library                            
                            """
                            #If the build system can include the root of the library automatically (e.g. Arduino)
                            if self.config["options"]["root_include"]:
                                nestingFile = 0
                            else:
                                nestingFile = self._get_nesting_level(file_dir)
                            new_path = self._build_relative_path(nestingFile, best_match)

                        logger.debug('Include Path %s changed to %s' % (include_file,new_path))
                        new_file += new_path
                        if not new_file.endswith("\\n"):
                            new_file += '''\n'''
                        found_new_path = True
                        paths_found += 1
            if not found_new_path:
                new_file += line
        if paths_found > 0:
            return new_file
        else:
            return None

    def run(self):
        file_list = self.__list_all_files(".")
        changed_files = 0
        for file in file_list:
            if file.suffix in self.file_ext:
                new_file = self._fixPaths(file)
                if new_file is not None:
                    logger.info('Updated %s' % file)
                    changed_files += 1
                    changed_file = open(file, "w")
                    changed_file.write(new_file)
                    changed_file.close()
        logger.info('Changed %d Files' % changed_files)
