
# MVP

- button to select single file, then if it is a
    - generic file: create asic-s with tst and ots
    - asic-s file: add/verify tst, then add/verify/upgrade/prune ots

---

# GUI Elements overview

## main window

- drag and drop area
- button to select single file
- tst on/off (configured/unconfigured)
- tst credit (if set on, configured, and API available)

## menu bar

- file menu
    - open (select single file to stamp - or upgrade/verify if it's asic-s)
    - quit
- settings
    - ots (box to edit ots servers list and minimum number of promises)
    - btc (node address and port to local verify - or a list of block explorer)
    - tst (box to set url, user, pwd)
    - opening (ots upgrade/prune, ask/auto/off)
- about

---

# Functions 1/2

## ots and tst

- ots
    - stamp
        - input: non asic file
        - output: ots file
    - upgrade | prune
        - input: ots file
        - output: ots file
    - verify
        - input: ots file
        - output: true | false
- tst
    - stamp
        - input: non asic file
        - output: tst file
    - verify
        - input: tst file
        - output: true | false

---

# Functions 2/2

## asic

- asic-s create
    - input/output: non asic-s file/asic-s new file
    - actions:
            - create asic-s structure
            - add mimetype, tst, ots (to tst)
            - zip (and set mimetype in archive comment)
- asic-s update
    - input/output: asic-s file old/verified+updated
    - actions:
            - extract
            - apply/verify tst (asic-s could contain just signature)
            - apply(to tst)/verify/upgrade/prune ots
            - zip
- asic-s check
    - input: file
    - output: true if asic-s | false if other (also asice-e or zip)
- open
    - input: file
    - actions:
        - if asic-s check is false: asic-s create
        - else: asic-s update
    - output:
        - updated asic-s
        - status/actions done on tst and ots

