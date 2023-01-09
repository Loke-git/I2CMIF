# I2CMIF
## Changelog
### 1.1.3 (current)
1. Restored functionality for notBefore and notAfter dates, visible in (among others) object BudatSA, for both outputs.

Note: Date spans are noted as DATE1%DATE2 in the JSON/CSV files (%-sep).

### 1.1.2
1. Output is now sent for another pass to remove linebreaks within tags.
2. Output source UUID is now prefixed with #.
   
### 1.1.1
1. Script will now recognise a CSV file containing "varia" (varia_file.csv). If detected, the script will output an additional set of files with the HTV suffix that include varia (miscellaneous) items, including greetings and dedications.
2. Script now uses the HT suffix to denote CMIF and metadata that only have the main texts included.
3. One UID is provided through config.ini and is made distinct for both outputs by appending HT or HTV depending on whether varia is included.

### 1.1.0
Previous CMIF versions are no longer compatible.

1. Script now uses Ruth Sander's compiled letter data to apply GeoNames IDs.
2. Script translates "UKJENT MOTTAGER" to "UNKNOWN RECIPIENT".
3. Fixed an error that would make the settlement element be recognised as place of origin for letters.
4. Made the console output a few more details (what GeoNames IDs we fetched, erroneous placenames).

### 1.0.0
1. Script now outputs a complete CMIF save for the lack of place name UIDs.
2. Included is the local ID for persons and letters, the URL of letters and persons (local in the sense that they use our webpages), dates, place names (not UIDs!) and to/from information wherever available.

## Introduction
Converts Ibsen letters to CMIF. The script is more or less a significantly simplified port of the work I did for eMunch's XML to CMIF project. Created by assistant researcher Loke Sjølie for the Centre for Ibsen Studies at the University of Oslo.

## Required files
### Letter files
The script requires one or more copies of the primary texts for letters (B1844-1871ht.xml, etc) in a subfolder called *letters*.
### Ruth Sander's Compiled Letter Data
The script currently requires a copy of Compiled_Letter_Data.csv in the same folder as the script file. This augments the CMIF with places' GeoNames IDs.

## Instructions
1. Place config.ini, I2CMIF.py in a folder
2. Edit config.ini to your liking
3. Place the letter files (B1844-1871ht.xml etc) in a **subfolder** called "letters"
4. Place the Compiled_Letter_Data.csv file in the same folder as the script file itself
5. Run I2CMIF.py

Essentially, just keep the folder structure as shown on this GitHub repository as-is, replacing any files as required. This outputs one CMIF file and one JSON file (or two, if a varia file is found).

## Known issues
1. ~~The script does NOT reference URLs where the individual document may be found online.~~ **The script now references where the documents may be found online.**
2. ~~The script does NOT have a complete URL to the place IDs, only an impartial local ID. I would replace these with GeoNames IDs.~~ **The script now references GeoNames IDs where possible.**
3. Some placenames in the primary texts, such as Budat18880514FinDep, do not provide an actual location ("KRISTIANIAMÜNCHEN"). These are treated as real places, but are not referenced by GeoNames IDs. These documents and IDs are, as of 2022-12-16:

['B18580604CHo', 'Budat1884Stort', 'Budat18880514FinDep', 'Budat189110NN_Opfordring']
['DAMPSKIPET CHRISTIANIA', 'KRISTIANIAROMA', 'KRISTIANIAMÜNCHEN', 'KRISTIANIABERGEN']
