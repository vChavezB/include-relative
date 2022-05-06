
# Relative Include

Python utility that replaces C/C++ `#include` directives with relative paths.  It searches for a set of include paths (typically provided by a build system) and searches for the best match and uses a relative path instead. Typically this wouldnt be required if you are using CMake, Meson, Make, etc, but if the build system does not allow to include directories paths, then you can only resort to relative includes.

## Motivation
The motivation of this script is that the [Arduino](https://www.arduino.cc/)  build system for libraries [does not](https://github.com/arduino/arduino-cli/issues/501) have an easy way to add include directories.  Instead libraries developed for the Arduino platform require to use relative paths. This should not be a problem if you are developing the library only for Arduino.  However, if you want to port a 3rd party library into Arduino in can be a PITA. 

If the 3rd party library has a few files it is not a problem but when the number increases, adding the relative paths can take too long or requires to change the original structure of the 3rd party library. If you need to update the library, then you need to repeat this process either because you changed the library structure or the authors of the library changed the place of the headers.


## Installation

Pip install

```bash
    python -m pip install relative_include
```

Local install

```bash
    python -m setup.py install
```

## Usage


Run the script 
```
    python -m relative_include
```

```bash
usage: [-h] [-s] [-d] [-V] config_file

positional arguments:
  config_file    JSON Config file to run this script

optional arguments:
  -h, --help     show this help message and exit
  -s             Silent output
  -d             Print debug messages
  -V, --version  show program's version number and exit
```

To use the script, a JSON configuration file must be provided with the following information

- `lib_path`: String Path where the C++/C project is located
- `include_paths`: string array that represents the relative path with respect to `lib_path` of where the include directories are located. Typically these values are passed to the compiler via the `-I` flag.
- `include_same_dir`: Boolean value that indicates wether include directives are included directly by the name of the file or must refer to the root of their directory.  By default set to true.
    For example,  if file `foo.c` includes `bar.h`, and are located in the directory `Foo`,  the include directive can either be 
	 - `#include "bar.h"`  when `include_same_dir` equals `true`
	 - `#include "../Foo/bar.h"` when `include_same_dir` equals `false`  

   The second option might seem unnecessary, but if you have another file named `bar.h` that is included via the compiler flag `-I`, the incorrect header with the same name might be included. I have seen this behaviour when porting the lwIP project to the Arduino platform and is left as an option for this specific type of edge cases.
- `out`: Dictionary Settings for the output of the script 
	- `dir`: String path that indicates wheree to write the output of the script with the relative include changes.
	- `overwrite` Bolean value that allows to overwrrite the output directory if it already exists.
- `silent`:  Boolean value. Silences the output of the script. By default set to false.
- `debug`: Boolean value. Prints debug information from the script. By default set to false.


