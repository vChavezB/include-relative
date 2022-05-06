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

"""
Usage:
------

usage: [-h] [-s] [-d] [-V] config_file

positional arguments:
  config_file    JSON Config file to run this script

optional arguments:
  -h, --help     show this help message and exit
  -s             Silent output
  -d             Print debug messages
  -V, --version  show program's version number and exit


"""
from .relative_include import RelativeIncludeCfg,RelativeInclude

def main() -> None:
    cfg = RelativeIncludeCfg.get_config()
    relative = RelativeInclude(cfg)
    relative.run()


if __name__ == "__main__":
    main()
