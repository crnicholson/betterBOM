# Kicad + Digikey Automation

import re
import digikey
from digikey.v3.productinformation import KeywordSearchRequest
import os
import ast
import sys

# Settings - THIS WILL CHANGE PER YOUR CONFIGURATION:
####################################################################
os.environ["DIGIKEY_CLIENT_ID"] = "your-client-id-here" # <- Register with DigiKey API
os.environ["DIGIKEY_CLIENT_SECRET"] = "your-client-secret-here" # <- ^
os.environ["DIGIKEY_STORAGE_PATH"] = "cache_dir" # Needed by DigiKey API
schematic_file_path = "demo/demo.kicad_sch" # Path to the schematic
####################################################################

# Get the component value field from KiCAD
def get_component_value(schematic_file, ref_des):
    try:
        with open(schematic_file, "r") as file:
            data = file.read() 

        # RegEx to pick out the value
        component_pattern = re.compile(
            r"\(symbol\n"
            r'\s+\(lib_id ".*?"\)\n'
            r"\s+\(at [^\)]+\)\n"
            r"\s+\(unit \d\)\n"
            r"\s+\(exclude_from_sim [^\)]+\)\n"
            r"\s+\(in_bom [^\)]+\)\n"
            r"\s+\(on_board [^\)]+\)\n"
            r"\s+\(dnp [^\)]+\)\n"
            r'\s+\(uuid "[^\)]+\"\)\n'
            r'(?:\s+\(property "Reference" "' + ref_des + r'".*?\))?\n'
            r'\s+\(property "Value" "([^"]+)"',
            re.MULTILINE | re.DOTALL,
        )

        # If found, return the value
        match = component_pattern.search(data)
        if match:
            return match.group(1)

        return None

    except FileNotFoundError:
        print(f"File {schematic_file} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Set the value field of the component in KiCAD
def set_component_value(schematic_file, ref_des, new_value):
    try:
        with open(schematic_file, "r") as file:
            data = file.read()

        # More RegEx to specify where to set the field
        component_pattern = re.compile(
            r"(\(symbol\n"
            r'\s+\(lib_id ".*?"\)\n'
            r"\s+\(at [^\)]+\)\n"
            r"\s+\(unit \d\)\n"
            r"\s+\(exclude_from_sim [^\)]+\)\n"
            r"\s+\(in_bom [^\)]+\)\n"
            r"\s+\(on_board [^\)]+\)\n"
            r"\s+\(dnp [^\)]+\)\n"
            r'\s+\(uuid "[^\)]+\"\)\n'
            r'(?:\s+\(property "Reference" "' + ref_des + r'".*?\))?\n'
            r'\s+\(property "Value" ")' + r'([^"]+)"',
            re.MULTILINE | re.DOTALL,
        )

        # If field found, set it!
        match = component_pattern.search(data)
        if match:
            new_data = data[: match.start(2)] + new_value + data[match.end(2) :]
            with open(schematic_file, "w") as file:
                file.write(new_data)
            return True

        return False

    except FileNotFoundError:
        print(f"File {schematic_file} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Get the reference designator from the command line
component_ref = str(sys.argv[1])
search = str(get_component_value(schematic_file_path, component_ref))

search_requests = KeywordSearchRequest(keywords=search, record_count=10)
results = digikey.keyword_search(body=search_requests)

# The JSON coming out of it is using single quotes, not the standard double quotes. Therefore, we use literal_eval()
parsed = ast.literal_eval(str(results))

outputDict = {}

# Create a nice, easy to parse dictionary
for i in range(len(parsed['products'])):
   
    # Create a new dictionary for each product
    product_dict = {
        'unit_price': str(parsed['products'][i]['unit_price']),
        'quantity': str(parsed['products'][i]['minimum_order_quantity']),
        'part_num': str(parsed['products'][i]['manufacturer_part_number'])
    }
    
    # Append the product dictionary to the output dictionary
    outputDict[i] = product_dict

# Filter out quantities greater than 10. In the future, we plan to accept the quantity as a command-line argument.
specified_quantity = 10
outputDict = {k: v for k, v in outputDict.items() if int(v['quantity']) <= specified_quantity}

# Print it all out!
print("Possible Parts:\n")
for key, value in outputDict.items():
    print(f"{key}. Part Number: {value['part_num']}, Unit Price: ${value['unit_price']}, Quantity: {value['quantity']}")

print(f"Best Product Based on Price: {outputDict[next(iter(outputDict))]['part_num']}, at ${outputDict[next(iter(outputDict))]['unit_price']}")
print("Assigning Value to Schematic Symbol Now...")
# Set the schematic value to append the part number
set_component_value(schematic_file_path, component_ref, str({outputDict[next(iter(outputDict))]['part_num']}).strip("{''}") + " - " + str(search))
print("Done!")
