
# Build instructions

## Env setup

Python3 is mandatory

`pip install -r requirements.txt`

Note: on some Linux pip install does not work for PyQt5
in that case it could have to be installed as distro package

See cryptography.io info to build python cryptography module

# Build


`pip install fbs`

Use `fbs freeze` to generate executable in the `target` folder

Use `fbs installer` to generate macOS and win installer in the `target` folder

To generate AppImage for any Linux distros `cd appimage; ./build.sh`

# Run from source

## GUI mode

Use `fbs run` to execute from the source in GUI mode

or

```
cd src/main/python
./timebags
```

## Command Line Interface mode

Pass one or more files as params to execute in CLI mode

```
cd src/main/python
./timebags <filename>
```

# Test suite

```
cd src/main/python
./test
```
