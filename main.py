# Kicad + Digikey Automation

import re
import digikey
from digikey.v3.productinformation import KeywordSearchRequest
import os
import ast
import sys

schematic_file_path = "hacknight_demo.kicad_sch"

def get_component_value(schematic_file, ref_des):
    try:
        with open(schematic_file, "r") as file:
            data = file.read() 

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


def set_component_value(schematic_file, ref_des, new_value):
    try:
        with open(schematic_file, "r") as file:
            data = file.read()

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
    
os.environ["DIGIKEY_CLIENT_ID"] = "QlnQBYLGQCUJPG2xAydT5zUbrSzsARya"
os.environ["DIGIKEY_CLIENT_SECRET"] = "pCN17uORphL5KIys"
os.environ['DIGIKEY_STORAGE_PATH'] = "cache_dir"

component_ref = str(sys.argv[1])
search = str(get_component_value(schematic_file_path, component_ref))

search_requests = KeywordSearchRequest(keywords=search, record_count=10)
results = digikey.keyword_search(body=search_requests)

parsed = ast.literal_eval(str(results))

outputDict = {}

for i in range(len(parsed['products'])):
   
    # Create a new dictionary for each product
    product_dict = {
        'unit_price': str(parsed['products'][i]['unit_price']),
        'quantity': str(parsed['products'][i]['minimum_order_quantity']),
        'part_num': str(parsed['products'][i]['manufacturer_part_number'])
    }
    
    # Append the duct dictionary to the output dictionary
    outputDict[i] = product_dict

specified_quantity = 10
outputDict = {k: v for k, v in outputDict.items() if int(v['quantity']) <= specified_quantity}

print("Possible Parts:\n")
for key, value in outputDict.items():
    print(f"{key}. Part Number: {value['part_num']}, Unit Price: ${value['unit_price']}, Quantity: {value['quantity']}")

print(f"Best Product Based on Price: {outputDict[next(iter(outputDict))]['part_num']}, at ${outputDict[next(iter(outputDict))]['unit_price']}")
print("Assigning Value to Schematic Symbol Now...")
set_component_value(schematic_file_path, component_ref, str({outputDict[next(iter(outputDict))]['part_num']}).strip("{''}") + " - " + str(search))
print("Done!")