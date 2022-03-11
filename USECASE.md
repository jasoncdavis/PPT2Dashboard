Powerpoint to Dashboard
=====================================

The Powerpoint to Dashboard project enables the user to provide a Microsoft Powerpoint (.pptx) file with data placeholder annotations to depict the location of variable data. The user also supplies a JSON-based data mapping file, presumably generated on a periodic basis and runs the Python script.

The Python script will extract the .pptx file to its XML components and perform string replacements using the user-supplied data mapping file. It will them repackage the files into a suitable .pptx, then run it through a Libreoffice Impress image converter of .pptx to .png. Finally the script creates a simple HTML file referencing the .png image and copies to the Apache web publishing directory.

The business driver for developing this was for Cisco customers that desired a way to have dynamic data overlaying building images or network topology representations. The model allows the user to leverage graphic artists or their own Powerpoint layout skills to create a dashboard specific to their need without extensive HTML/CSS skills. The use of simple variable placeholders serve as reference points for the script to string-replace in the dynamic data.

## White Papers and References
Not applicable

## Related Sandbox
Not applicable

## Links to DevNet Learning Labs
Not applicable

## Solutions on Ecosystem Exchange
Not applicable