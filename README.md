# Better BOM - A Better Way to do KiCAD Part Finding

Better BOM takes your current schematic design - without part numbers - and finds the cheapest option available at the same time editing your schematic, all automatically. Created by Charlie Nicholson and Max Kendall at the HacKnight Hackathon.

# Getting Started

## API

Apply for an API key on the Digikey website, and make sure to create an organization with a production app. Learn more here.

## Dependencies

All the normal stuff you get with Python, and then <code>pip3 install digikey-api</code>.

## Running the Code

You can run the script by doing <code>python3 main.py your-reference-designator-here your-parameters-here</code>. For example, you could do capacitor C1 with a package of 0805: <code>python3 main.py C1 0805</code>.

The correct variables have to be set beforehand, including the API keys. Make sure this is done or else the program will not work. You can learn more [here](https://github.com/peeter123/digikey-api).

You will also need to change the path to your KiCAD schematic in the code. 

# The Future

If you want to help out, here are some things you can do!

We are planning on making a KiCAD plugin for the tool so you never need to leave the editor. We also want to implement batch method where it takes the current BOM and finds good parts for it. Then, we want to implement SnapEDA into it so we have a large database of footprints that would be installed automatically and entered with the part number retrieval. After that, we want to access the datasheets and use ChatGPT to find the all the reference designs and automatically place those in KiCAD as images for even faster design. Finally, we want to get ChatGPT into our plugin so we it can give recommendations for more advanced chip sets and it can tell us how to use them. 

# License

This code is licensed under the MIT license. Pull requests are welcome and encouraged. 