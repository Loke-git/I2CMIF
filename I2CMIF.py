#!/usr/bin/env python
# coding: utf-8
# version: 1.1.3
# by Loke Sjølie
# project uses code from Munch XML Muncher with permission
print("Initializing...")
import sys
import subprocess
import pkg_resources
print("Checking requirements...")
# Package installation borrowed from:
# https://stackoverflow.com/questions/12332975/installing-python-module-within-code/58040520#58040520
required  = {'bs4', 'pandas'} 
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed
if missing:
    # implement pip as a subprocess:
    print("\tInstalling requirements...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
else:
    print("\tRequirements met.")

# Ibsen XML Muncher 1
# Much of this code has been appropriated from the Munch XML Muncher (MXMLM) tool.
    
print("Importing libraries...")
import os
import pandas as pd
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import json

# File and folder handling
import glob # The yeast of thought and mind
import os # File system

# Metadata and configuration
import configparser # Used to easily get statements from the config file

# Time and date
from datetime import date

today = date.today()
today = today.strftime("%Y-%m-%d") # Formater dato

df = pd.read_csv("Compiled_Letter_Data.csv", sep=",")
df = df[['Dispatch_Location',"GeoName_ID"]].fillna("N/A")
placeIDdict = defaultdict(dict)
places = []
for idx,row in df.iterrows():
    place = str(row['Dispatch_Location'])
    place = place.lstrip('[').rstrip("]").upper()
    if place not in places:
        if str(row['GeoName_ID']) != "N/A":
            places.append(place)
            placeid = str(row['GeoName_ID']).split(".")
            placeid = placeid[0]
            placeIDdict[place] = placeid

            
print("\nGetting metadata from config.ini...")
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
cmifTitle = config.get("statements", "cmifTitle")
editorName = config.get("statements", "editorName")
editorMail = config.get("statements", "editorMail")
cmifUid = config.get("statements", "cmifUid")
publisherURL = config.get("statements", "publisherURL")
publisherName = config.get("statements", "publisherName")
cmifURL = config.get("statements", "cmifURL")
typeOfBibl = config.get("statements", "typeOfBibl")
publicationStatementFull = config.get("statements", "publicationStatementFull")
outputFileName = config.get("statements", "outputFileName")
outputFileNameVaria = config.get("statements", "outputFileNameVaria")

print(f"{cmifTitle}\nUID: {cmifUid}\nEditor: {editorName} ({editorMail}) at {publisherName} ({publisherURL})\n{publicationStatementFull}\nOutput: {outputFileName}.xml (main texts only) and {outputFileNameVaria}.xml (main texts and varia)")
t = "Targeting these files: "
listXMLfiles = glob.glob("letters/*.xml",recursive=True)
i=0
for file in listXMLfiles:
    if i!= 0:
        t += ", "
    t+=str(file)
    i+=1
print(t)
main = defaultdict(dict)

i=0

for xml_file in listXMLfiles:
    pathSplit = xml_file.split("\\")
    fileName = pathSplit[1]
    fileName = fileName.split(".")
    fileName = str(fileName[0])
    fileName = "https://www.ibsen.uio.no/BREV_"+fileName[1:]
    print("Melting",xml_file)
    with open(xml_file, "r", encoding="utf-8") as file:
        # Read each line in the file, readlines() returns a list of lines
        content = file.readlines()
        # Combine the lines in the list into a string
        content = "".join(content)
        soup = bs(content, "xml")
    for document in soup.findAll('HIS:hisMsDesc', {"xml:id":True}):
        theAuthorsRefs,theAuthors,theAuthorsTypes,theRecipients,theRecipientsRefs,theRecipientsTypes = [],[],[],[],[],[]
        docType = list(document.attrs.values())[0]
        docID = list(document.attrs.values())[1]
        printString = str(docID)
        
        try:
            docLoc = document.find("origPlace").findChild("HIS:hisRef", {"type":"place"}).contents[0]
            place = document.find("origPlace").findChild("HIS:hisRef", {"type":"place"})
            placeID = list(place.attrs.values())[1]
            placeID = placeID.replace("Navneregister_HISe.xml#","")

        except:
            docLoc = "UKJENT OPPRINNELSESSTED"
            placeID = "plNN"
        printString+=", "+docType+" from "+docLoc

        isDocumentFromTo = document.find("origDate", {"notBefore":True}) # Does the date element have a not before assignment? 
        if isDocumentFromTo: # If it does, and thus has a range
            doesDocumentHaveToDate = document.find("origDate", {"notAfter":True})
            if doesDocumentHaveToDate:
                # Both from and to attributes are present.
                fromDate = isDocumentFromTo['notBefore'] # Extract 'from' date. 
                toDate = isDocumentFromTo['notAfter'] # Extract 'to' date.
                date = str(fromDate)+"%"+str(toDate)
            else:
                # If the 'from' attribute is present without the 'to', it's interpreted as "not before this date". This is unlikely in Ibsen files; here as an in-case.
                date = isDocumentFromTo['notBefore']
        else:
            dateObj = document.find("origDate")
            date = list(dateObj.attrs.values())[0]
        printString+=" dated: "+date
        printString+="\n"
        senders = document.find("name",{"role":"sender"}).findChildren(True, recursive=True)
        printString+="Senders: "
        for sender in senders:
            senderType = list(sender.attrs.values())[0]
            senderRef = list(sender.attrs.values())[1]
            senderRef = senderRef.replace("Navneregister_HISe.xml#","")
            for senderName in sender.contents:
                printString+=senderName+" ("+senderType+")"
                theAuthors.append(senderName)
                theAuthorsTypes.append(senderType)
                theAuthorsRefs.append(senderRef)
        recips = document.find("name",{"role":"recipient"}).findChildren(True, recursive=True)
        printString+=" | Recipients: "
        for recip in recips:
            recipType = list(recip.attrs.values())[0]
            recipRef = list(recip.attrs.values())[1]
            recipRef = recipRef.replace("Navneregister_HISe.xml#","")
            for recipName in recip.contents:
                printString+=recipName+" ("+recipType+")"
                theRecipients.append(recipName)
                theRecipientsTypes.append(recipType)
                theRecipientsRefs.append(recipRef)
                
        docLoc = docLoc.lstrip('[').rstrip("]").upper()
        
        if docLoc in placeIDdict:
            placeID = placeIDdict[docLoc]
        else:
            placeID = "N/A"
        main[docID]['type'] = docType
        main[docID]['date'] = date
        main[docID]['from'] = theAuthors
        main[docID]['fromRef'] = theAuthorsRefs
        main[docID]['fromType'] = theAuthorsTypes
        main[docID]['to'] = theRecipients
        main[docID]['toRef'] = theRecipientsRefs
        main[docID]['toType'] = theRecipientsTypes
        main[docID]['place'] = docLoc
        main[docID]['placeRef'] = placeID
        main[docID]['source'] = fileName+"|"+docID+".xhtml"

        i+=1
print("Acquired GeoNames IDs for these places:")
print(list(placeIDdict.keys()))
df1 = pd.DataFrame.from_dict(main).T.reset_index(drop=False)
df1.columns = "document","type","date","fromX","fromRef","fromType","to","toRef","toType","place","placeRef","source"

# Varia (miscellany) metadata harvesting 
print("Checking for varia_file.csv...")
if os.path.exists("varia_file.csv"):
    print("Processing varia...")
    old_links = ["https://www.ibsen.uio.no/VAR_V18901219HeG.xhtml","https://www.ibsen.uio.no/VAR_V1858kongO2.xhtml","https://www.ibsen.uio.no/VAR_V18930718EPh.xhtml","https://www.ibsen.uio.no/VAR_V18690926HSTp.xhtml","https://www.ibsen.uio.no/VAR_V1860Skand.xhtml","https://www.ibsen.uio.no/VAR_V1861Skand.xhtml","https://www.ibsen.uio.no/VAR_1862Skand.xhtml"]
    i=0
    warned_about_old_links = False
    supplement = defaultdict(dict)
    varia = pd.read_csv("varia_file.csv",sep=",").set_index("index")
    varia = varia.fillna("N/A")
    for idx,row in varia.iterrows():
        recipientID = row['fullID']
        if recipientID != "N/A":
            i+=1
            title,date,recipient,docType = row['title'],row['date'],row['clearname'],row['type']
            link = "https://www.ibsen.uio.no/VAR_"+str(idx)+".xhtml"
            recipRef = "https://www.ibsen.uio.no/REGINFO_"+str(recipientID)+".xhtml"
            if "pe" in recipientID:
                recipType = "person"
            elif "org" in recipientID:
                recipType = "org"
            #print(f"{idx}\n\t{title} from Ibsen to {recipient}, dated {date}\n\t{recipRef}\n\t{link}")
            supplement[idx]['type'] = docType
            supplement[idx]['date'] = date
            supplement[idx]['from'] = ["HENRIK IBSEN"]
            supplement[idx]['fromRef'] = ["peHI"]
            supplement[idx]['fromType'] = ["person"]
            supplement[idx]['to'] = [recipient]
            supplement[idx]['toRef'] = [recipientID]
            supplement[idx]['toType'] = [recipType]
            supplement[idx]['place'] = "N/A"
            supplement[idx]['placeRef'] = "N/A"
            supplement[idx]['source'] = link
            if link in old_links:
                if warned_about_old_links == False:
                    print("\n>> Warning: the CMIF will use links valid in 2022, meaning that the correct global person/institution ID (e.g. orgSF) is referred to as the old varia-specific ID (e.g. Skand) in the document IDs. Modify the source CSV with new links if applicable, or change them after the fact in the CMIF.")
                    warned_about_old_links = True
                print("\t"+link+" ("+recipRef+")")
    if warned_about_old_links == True:
        print("This warning will cease once the script does not detect the above links.")
    print(f"\nAcquired {i} items from varia.\nRemember! These links will only work as long as they're in the ibsen.uio.no/VAR_ domain.\n")
    df2 = pd.DataFrame.from_dict(supplement).T.reset_index(drop=False).fillna("N/A")
    df2.columns = "document","type","date","fromX","fromRef","fromType","to","toRef","toType","place","placeRef","source"
    df3 = df1.append(df2, ignore_index=True).reset_index(drop=True)
    df4 = df3.copy().set_index("document")
    df4_json = df4.to_json(orient="index")
# End varia metadata harvesting

# Standard CMIF (all normal letter correspondence)
# Append to UID..
cmifUid = cmifUid + "HT"
# Catch documents with weird/combined placenames in these
letters_with_weird_placenames,weird_placenames_in_letters = [],[]
print("Creating standard CMIF...")
# Create CMIF boilerplate object
CMIFstring = '<?xml-model href="https://raw.githubusercontent.com/TEI-Correspondence-SIG/CMIF/master/schema/cmi-customization.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt><title>'+str(cmifTitle)+'</title><editor>'+str(editorName)+'<email>'+str(editorMail)+'</email></editor></titleStmt><publicationStmt><publisher><ref target="'+str(publisherURL)+'">'+str(publisherName)+'</ref></publisher><idno type="url">'+str(cmifURL)+'</idno><date when="'+str(today)+'"/><availability><licence target="https://creativecommons.org/licenses/by/4.0/">This file is licensed under the terms of the Creative-Commons-License CC-BY 4.0</licence></availability></publicationStmt><sourceDesc><bibl type="'+str(typeOfBibl)+'" xml:id="'+str(cmifUid)+'">'+str(publicationStatementFull)+'</bibl></sourceDesc></fileDesc><profileDesc><dummy/></profileDesc></teiheader><text><body><p/></body></text></tei>'
CMIF = bs(CMIFstring,"xml") # Read as XML, not HTML
profileDescElement = CMIF.find('profileDesc') # Target correspondence wrapper


## PATCH
print("Applying February 2023 patch...")
df_People = pd.read_csv("Person_Register_Info.csv", sep=",")
df_People = df_People.fillna("N/A")
peopleVIAFdict = defaultdict(dict)

for idx,row in df_People.iterrows():
    viafID = row['Viaf_ID']
    xmlID = row['XML_ID']
    if viafID != "N/A":
        viafURL = "https://viaf.org/viaf/"+viafID
        peopleVIAFdict[xmlID] = viafURL


for idx,row in df1.iterrows():
    document,date,fromX,to,place,placeRef,source = row['document'],row['date'],row['fromX'],row['to'],row['place'],row['placeRef'],row['source']
    
    # Construct CMIF correspDesc element
    correspDescElement = CMIF.new_tag("correspDesc", attrs={"key":str(document), "ref":source, "source":"#"+cmifUid})
    profileDescElement.append(correspDescElement)
    i=0
    ## Author (sender) encoding
    
    for each in fromX:
        # For each author, add a correspAction element...
        correspActionElement = CMIF.new_tag("correspAction", attrs={'type':'sent'})
        correspDescElement.append(correspActionElement)
        category = df1.iloc[idx]["fromType"][i]
        ttX = df1.iloc[idx]["fromRef"][i]
        if ttX in peopleVIAFdict:
            ref = peopleVIAFdict[ttX]
        else:
            ref = str("https://www.ibsen.uio.no/REGINFO_")+str(df1.iloc[idx]["fromRef"][i])+str(".xhtml")
        if category == "org":
            if ref != "N/A":
                persNameElement = CMIF.new_tag("orgName", attrs={"ref":ref})
            else:
                persNameElement = CMIF.new_tag("orgName")
        else:
            if ref != "N/A":
                persNameElement = CMIF.new_tag("persName", attrs={"ref":ref})
            else:
                persNameElement = CMIF.new_tag("persName")
        persNameElement.string = str(each)
        correspActionElement.append(persNameElement)
        i+=1
    # Place encoding
    if place != "N/A" and place != "UKJENT OPPRINNELSESSTED":
        if placeRef != "N/A" and placeRef != "plNN":
            locationElement = CMIF.new_tag("placeName", attrs={"ref":"http://www.geonames.org/"+placeRef}) # Create place element
        else:
            locationElement = CMIF.new_tag("placeName")#, attrs={"ref":placeRef} # Create place element
            letters_with_weird_placenames.append(document)
            weird_placenames_in_letters.append(place)
        locationElement.string = str(place) # Give it a string value (placename)
        correspActionElement.append(locationElement) # Append the new element to the correspAction element
    # End place encoding
    # Date encoding
    if date != "N/A":
        if "%" in str(date): # If this is a "split" (uncertain) date:
            dateObject = date.split("%")
            dateSentElement = CMIF.new_tag("date", attrs={"notBefore":dateObject[0], "notAfter":dateObject[1]}) # Construct element with notbefore and notafter attributes
            correspActionElement.append(dateSentElement)
        else: # If this is a simple date:
            dateSentElement = CMIF.new_tag("date", attrs={"when":date})
            correspActionElement.append(dateSentElement)
    # End date encoding
    # End author (sender) encoding
    
    i=0
    # Recipient encoding
    for each in to:
        correspActionElement = CMIF.new_tag("correspAction", attrs={'type':'received'})
        correspDescElement.append(correspActionElement)
        category = df1.iloc[idx]["toType"][i]
        ttX = df1.iloc[idx]["fromRef"][i]
        if ttX in peopleVIAFdict:
            ref = peopleVIAFdict[ttX]
        else:
            ref = str("https://www.ibsen.uio.no/REGINFO_")+str(df1.iloc[idx]["toRef"][i])+str(".xhtml")
        #ref = df1.iloc[idx]["toRef"][i]
        if each == "UKJENT MOTTAGER":
            each = "UNKNOWN RECIPIENT"
        if category == "org":
            if ref != "N/A":
                persNameElement = CMIF.new_tag("orgName", attrs={"ref":ref})
            else:
                persNameElement = CMIF.new_tag("orgName")
        else:
            if ref != "N/A":
                persNameElement = CMIF.new_tag("persName", attrs={"ref":ref})
            else:
                persNameElement = CMIF.new_tag("persName")
        i+=1
        persNameElement.string = str(each)
        correspActionElement.append(persNameElement)

    # End recipient encoding

dummyElement = CMIF.find("dummy").decompose() # This will destroy the <dummy/> element.

print("Saving output...")
CMIFstr = str(CMIF)
CMIF = bs(CMIFstr, "xml", preserve_whitespace_tags=["placeName","bibl","corresp","title","persName","editor","email","publisher","ref","idno","licence"])
with open(outputFileName+".xml", "w", encoding="utf-8") as outfile:
    outfile.write(CMIF.prettify())

print("Done exporting CMIF as",outputFileName)
with open("ibsen-correspondence-metadata_ht.json", "w") as outfile:
    json.dump(main, outfile, indent = 4)
print("Saved metadata in ibsen-correspondence-metadata_ht.json")

if len(weird_placenames_in_letters) > 0:
    print(f"\nThese documents have strange placenames:\n{letters_with_weird_placenames}\n{weird_placenames_in_letters}")
    
# End standard CMIF


if os.path.exists("varia_file.csv"):
    # Experimental standard + varia CMIF

    # Catch documents with weird/combined placenames in these
    letters_with_weird_placenames,weird_placenames_in_letters = [],[]
    print("\n\nCreating varia-augmented CMIF...")
    # Change the UID..
    cmifUid = cmifUid + "V"
    # Create CMIF boilerplate object
    CMIFstring = '<?xml-model href="https://raw.githubusercontent.com/TEI-Correspondence-SIG/CMIF/master/schema/cmi-customization.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt><title>'+str(cmifTitle)+'</title><editor>'+str(editorName)+'<email>'+str(editorMail)+'</email></editor></titleStmt><publicationStmt><publisher><ref target="'+str(publisherURL)+'">'+str(publisherName)+'</ref></publisher><idno type="url">'+str(cmifURL)+'</idno><date when="'+str(today)+'"/><availability><licence target="https://creativecommons.org/licenses/by/4.0/">This file is licensed under the terms of the Creative-Commons-License CC-BY 4.0</licence></availability></publicationStmt><sourceDesc><bibl type="'+str(typeOfBibl)+'" xml:id="'+str(cmifUid)+'">'+str(publicationStatementFull)+'</bibl></sourceDesc></fileDesc><profileDesc><dummy/></profileDesc></teiheader><text><body><p/></body></text></tei>'
    CMIF = bs(CMIFstring,"xml") # Read as XML, not HTML
    profileDescElement = CMIF.find('profileDesc') # Target correspondence wrapper
    for idx,row in df3.iterrows():
        document,date,fromX,to,place,placeRef,source = row['document'],row['date'],row['fromX'],row['to'],row['place'],row['placeRef'],row['source']

        # Construct CMIF correspDesc element
        correspDescElement = CMIF.new_tag("correspDesc", attrs={"key":str(document), "ref":source, "source":"#"+cmifUid})
        profileDescElement.append(correspDescElement)
        i=0
        ## Author (sender) encoding

        for each in fromX:
            # For each author, add a correspAction element...
            correspActionElement = CMIF.new_tag("correspAction", attrs={'type':'sent'})
            correspDescElement.append(correspActionElement)
            category = df3.iloc[idx]["fromType"][i]
            ttX = df3.iloc[idx]["fromRef"][i]
            if ttX in peopleVIAFdict:
                ref = peopleVIAFdict[ttX]
            else:
                ref = str("https://www.ibsen.uio.no/REGINFO_")+str(df3.iloc[idx]["fromRef"][i])+str(".xhtml")
            if category == "org":
                if ref != "N/A":
                    persNameElement = CMIF.new_tag("orgName", attrs={"ref":ref})
                else:
                    persNameElement = CMIF.new_tag("orgName")
            else:
                if ref != "N/A":
                    persNameElement = CMIF.new_tag("persName", attrs={"ref":ref})
                else:
                    persNameElement = CMIF.new_tag("persName")
            persNameElement.string = str(each)
            correspActionElement.append(persNameElement)
            i+=1
        # Place encoding
        if place != "N/A" and place != "UKJENT OPPRINNELSESSTED":
            if placeRef != "N/A" and placeRef != "plNN":
                locationElement = CMIF.new_tag("placeName", attrs={"ref":"http://www.geonames.org/"+placeRef}) # Create place element
            else:
                locationElement = CMIF.new_tag("placeName")#, attrs={"ref":placeRef} # Create place element
                letters_with_weird_placenames.append(document)
                weird_placenames_in_letters.append(place)
            locationElement.string = str(place) # Give it a string value (placename)
            correspActionElement.append(locationElement) # Append the new element to the correspAction element
        # End place encoding
        # Date encoding
        if date != "N/A":
            if "%" in str(date): # If this is a "split" (uncertain) date:
                dateObject = date.split("%")
                dateSentElement = CMIF.new_tag("date", attrs={"notBefore":dateObject[0], "notAfter":dateObject[1]}) # Construct element with notbefore and notafter attributes
                correspActionElement.append(dateSentElement)
            else: # If this is a simple date:
                dateSentElement = CMIF.new_tag("date", attrs={"when":date})
                correspActionElement.append(dateSentElement)
        # End date encoding
        # End author (sender) encoding

        i=0
        # Recipient encoding
        for each in to:
            correspActionElement = CMIF.new_tag("correspAction", attrs={'type':'received'})
            correspDescElement.append(correspActionElement)
            category = df3.iloc[idx]["toType"][i]
            ttX = df3.iloc[idx]["fromRef"][i]
            if ttX in peopleVIAFdict:
                ref = peopleVIAFdict[ttX]
            else:
                ref = str("https://www.ibsen.uio.no/REGINFO_")+str(df3.iloc[idx]["toRef"][i])+str(".xhtml")
            #ref = df3.iloc[idx]["toRef"][i]
            if each == "UKJENT MOTTAGER":
                each = "UNKNOWN RECIPIENT"
            if category == "org":
                if ref != "N/A":
                    persNameElement = CMIF.new_tag("orgName", attrs={"ref":ref})
                else:
                    persNameElement = CMIF.new_tag("orgName")
            else:
                if ref != "N/A":
                    persNameElement = CMIF.new_tag("persName", attrs={"ref":ref})
                else:
                    persNameElement = CMIF.new_tag("persName")
            i+=1
            persNameElement.string = str(each)
            correspActionElement.append(persNameElement)

        # End recipient encoding

    dummyElement = CMIF.find("dummy").decompose() # This will destroy the <dummy/> element.

    print("Saving output...")
    CMIFstr = str(CMIF)
    CMIF = bs(CMIFstr, "xml", preserve_whitespace_tags=["orgName","placeName","bibl","corresp","title","persName","editor","email","publisher","ref","idno","licence"])
    with open(outputFileNameVaria+".xml", "w", encoding="utf-8") as outfile:
        outfile.write(CMIF.prettify())

    print("Done exporting CMIF as",outputFileNameVaria)


    parse_json = json.loads(df4_json)
    with open("ibsen-correspondence-metadata_htv.json", "w") as outfile:
        json.dump(parse_json, outfile, indent = 4)
    print("Saved metadata in ibsen-correspondence-metadata_htv.json")

    if len(weird_placenames_in_letters) > 0:
        print(f"\nThese documents have strange placenames:\n{letters_with_weird_placenames}\n{weird_placenames_in_letters}")

    # End experimental CMIF



print("All done! Have a nice day.")


