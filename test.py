# import xml.etree.ElementTree as ET
# from datetime import datetime, timedelta

# def parse_tides(file_path):
#     """Parse tide data from an XML file with debug print statements."""
#     print("Parsing tide data from XML file...")
#     tree = ET.parse(file_path)
#     root = tree.getroot()
#     tide_data = []

#     # Iterate over <value> elements to extract tide information
#     for entry in root.find('values'):
#         dt = datetime.strptime(entry.find('datetime').text.strip(), "%Y%m%d%H%M")
#         tide = entry.find('tide').text.strip()  # HW or LW
#         val = int(entry.find('val').text.strip())
#         # print(f"Found tide entry - DateTime: {dt}, Tide: {tide}, Value: {val}")
#         tide_data.append((dt, tide, val))

#     # Sort by datetime to ensure order
#     tide_data.sort(key=lambda x: x[0])
#     print("Tide data sorted by datetime.")
#     # for entry in tide_data:
#         # print(f"Tide entry - DateTime: {entry[0]}, Tide: {entry[1]}, Value: {entry[2]}")
    
#     return tide_data

# def find_current_tide_phase(tide_data):
#     """Find the current tide regime based on tide data with debug print statements."""
#     now = datetime.now()
#     print(f"Current datetime: {now}")
    
#     # Find the nearest low and high tide before and after current time
#     previous_tide = None
#     next_tide = None
    
#     for i in range(len(tide_data) - 1):
#         # print(f"Checking tide data entry {i} - DateTime: {tide_data[i][0]}")
        
#         if tide_data[i][0] <= now <= tide_data[i + 1][0]:
#             previous_tide = tide_data[i]
#             next_tide = tide_data[i + 1]
#             # print("Found surrounding tides:")
#             # print(f"Previous Tide - DateTime: {previous_tide[0]}, Tide: {previous_tide[1]}, Value: {previous_tide[2]}")
#             # print(f"Next Tide - DateTime: {next_tide[0]}, Tide: {next_tide[1]}, Value: {next_tide[2]}")
#             break
    
#     # If no surrounding tides found (boundary case), return None
#     if not previous_tide or not next_tide:
#         print("No surrounding tides found. Boundary case detected.")
#         return None

#     # Calculate time difference between previous and next tide
#     time_diff = (next_tide[0] - previous_tide[0]).total_seconds()
#     elapsed_time = (now - previous_tide[0]).total_seconds()
#     phase_position = elapsed_time / time_diff
    
#     print(f"Time difference between tides: {time_diff} seconds")
#     print(f"Elapsed time since previous tide: {elapsed_time} seconds")
#     print(f"Phase position (elapsed / total): {phase_position:.2f}")

#     # Determine the tide regime based on the phase position
#     if previous_tide[1] == "LW" and next_tide[1] == "HW":
#         print("Transitioning from Low to High Tide.")
#         if phase_position < 0.5:
#             print("Current tide phase: low-mid (lm)")
#             return "lm"  # low-mid
#         else:
#             print("Current tide phase: mid-high (mh)")
#             return "mh"  # mid-high
#     elif previous_tide[1] == "HW" and next_tide[1] == "LW":
#         print("Transitioning from High to Low Tide.")
#         if phase_position < 0.5:
#             print("Current tide phase: high-mid (hm)")
#             return "hm"  # high-mid
#         else:
#             print("Current tide phase: mid-low (ml)")
#             return "ml"  # mid-low

# # Example usage:
# tide_data = parse_tides("C:/Github/surfconditions_database/hwlw-SCHEVNGN-20240101-20241231.xml")
# current_tide_phase = find_current_tide_phase(tide_data)
