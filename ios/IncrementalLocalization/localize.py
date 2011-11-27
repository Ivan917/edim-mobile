import sys
import subprocess
import getopt
import os.path

options, idioms = getopt.getopt(sys.argv[1:], "", ["mainStoryboard=", "mainIdiom="])

#retrieve parameters
for option1, option2 in options:
    if option1 == "--mainIdiom":
        mainIdiom = option2
    elif option1 == "--mainStoryboard":
        newMainStoryboard = option2
        oldMainStoryboard = newMainStoryboard.replace(".storyboard", "_old.storyboard")
        
        #if the old mainStoryboard is not created, create it
        if not os.path.exists(oldMainStoryboard):
            subprocess.call(["cp", newMainStoryboard, oldMainStoryboard])

errorDescription = ""

for idiom in idioms:
    #paths of files for current idiom
    idiomNewStoryboard = newMainStoryboard.replace(mainIdiom + ".lproj", idiom + ".lproj")
    idiomOldStoryboard = idiomNewStoryboard.replace(".storyboard", "_old.storyboard")
    idiomStringsFile = idiomNewStoryboard.replace(".storyboard", ".strings")

    #if the storyboard for the current idiom dont exists, add an error to be show to the user
    if not os.path.exists(idiomNewStoryboard):
        errorDescription += "\n*** You need to add create the '" + idiomNewStoryboard + "' in interface builder*** \n"
    else:
        #copy the storyboard to the old storyboard (current idiom)
        subprocess.call(["cp", idiomNewStoryboard, idiomOldStoryboard])
        
        #if the strings file (current idiom) dont exists, create it
        if not os.path.exists(idiomStringsFile):
            subprocess.call(["ibtool",
                     "--generate-strings-file", idiomStringsFile,
                     idiomNewStoryboard])

        #generates the incremental storyboard (current idiom)
        if subprocess.call(["ibtool", 
                         "--previous-file", oldMainStoryboard,
                         "--incremental-file", idiomOldStoryboard,
                         "--strings-file", idiomStringsFile,
                         "--localize-incremental",
                         "--write", idiomNewStoryboard,
                                newMainStoryboard]) == 0:
            
            #generates the strings file (current idiom), to be used on the next build
            subprocess.call(["ibtool",
                         "--generate-strings-file", idiomStringsFile,
                         idiomNewStoryboard])
        
        #if an error occurred, add an error to be show to the user
        else:
            errorDescription += "\n*** Error while creating the '" + idiomNewStoryboard + "' file*** \n"


#Copy the main storyboard to the old one (main idiom) to be used on the next build
subprocess.call([ "cp", newMainStoryboard, oldMainStoryboard])

#generates the strings file (main idiom), to be used on the next build
subprocess.call(["ibtool",
                 "--generate-strings-file", newMainStoryboard.replace(".storyboard", ".strings"),
                 newMainStoryboard])

#if an error occurred, throws an exception to fail the build process
if errorDescription != "":
    raise Exception("\n" + errorDescription)