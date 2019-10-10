
# MVP

- button to select single file
- from a generic file create asic-s with ots

---

# GUI Elements overview

## main window

- drag and drop area
- button to select single file
- tsa on/off
- tsa credit (if set on, configured, and API available)

## menu bar

- file menu
    - open (select single file to stamp - or upgrade/verify if it's asic-e/s)
    - quit
- settings
    - ots (box to edit ots servers list and minimum number of promises)
    - btc (node address and port to local verify - or a list of block explorer)
    - tsa (box to set url, user, pwd)
- about

---

# Functions 1/2

## ots and tsa

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
- tsa
    - stamp
        - input: non asic file
        - output: tsr file
    - verify
        - input: tsr file
        - output: true | false

---

# Functions 1/2

## asic

- create asic
    - input: files, tsr, ots, xml 
    - output: asic-e new file
- detect asic
    - input: file 
    - output: status = asic-e | asic-s | zip | non zip
- open asic
    - input: asic-e/s
    - actions: 
        - verify tsr 
        - verify/upgrade/prune ots
        - apply missed tsr
        - apply missed ots (also to tsr)
    - output: 
        - updated asic-e
        - status of tsa and ots stamps found
        - list of actions done:
            - tsa and/or ots applied if absent
            - ots upgraded and/or pruned if incomplete
