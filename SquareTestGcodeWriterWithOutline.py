import os
def generate_gcode(scan_speeds, line_spacings, filename):
    gcode = []
    scan_time_sec = 0.0
    pass_counter = 1

    # Function to move to a point with laser off
    def move_to(x, y):
        gcode.append("M5 ; Laser Off")
        gcode.append(f"G0 X{x:.2f} Y{y:.2f} F3000")

    # Function to move to a point with laser on
    def laser_move_to(x, y, speed):
        gcode.append("M3 S255 ; Laser On")
        gcode.append("G4 P200") #Wait 200 milliseconds for laser to turn on
        gcode.append(f"G1 X{x:.2f} Y{y:.2f} F{speed*60:.2f}")
        gcode.append("G4 P200") #Wait 200 milliseconds for laser to turn off
        gcode.append("M5 ; Laser Off")

    # Initialize the GCode
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Use absolute positioning")
    gcode.append("G28 X0 Y0 Z0")
    gcode.append("RECOATER_PUSH")
    gcode.append("RECOATER_PULL")

    # Squares parameters
    square_size = 20
    square_spacing = 5
    squares_max_x = 100
    squares_min_y = 260
    

    # Generate GCode for each row of squares
    for row in range(3):
        # Get the line spacing for the current row of squares
        current_line_spacing = line_spacings[row % len(line_spacings)]
        # Calculate the number of lines to scan within each square
        num_lines = int((square_size - (2*(0.7*current_line_spacing))) / current_line_spacing)
        move_to(squares_max_x,squares_min_y+(row*25))
        # First Column of Row Outline
        laser_move_to(squares_max_x - 20, squares_min_y + (row*25), 3)
        laser_move_to(squares_max_x - 20, squares_min_y + (row*25) + 20, 1)
        laser_move_to(squares_max_x, squares_min_y + (row*25) + 20, 3)
        laser_move_to(squares_max_x, squares_min_y + (row*25), 1)
        # Second Column of Row Outline
        move_to(squares_max_x - 25,squares_min_y+(row*25))
        laser_move_to(squares_max_x - 20 - 25, squares_min_y + (row*25), 3)
        laser_move_to(squares_max_x - 20 - 25, squares_min_y + (row*25) + 20, 1)
        laser_move_to(squares_max_x - 25, squares_min_y + (row*25) + 20, 3)
        laser_move_to(squares_max_x - 25, squares_min_y + (row*25), 1)
        # Thirst Column of Row Outline
        move_to(squares_max_x - 50,squares_min_y+(row*25))
        laser_move_to(squares_max_x - 20 - 50, squares_min_y + (row*25), 3)
        laser_move_to(squares_max_x - 20 - 50, squares_min_y + (row*25) + 20, 1)
        laser_move_to(squares_max_x - 50, squares_min_y + (row*25) + 20, 3)
        laser_move_to(squares_max_x - 50, squares_min_y + (row*25), 1)
        for pass_counter in range(2):
            # For each line within the row
            for line_index in range(num_lines):
                if (((pass_counter == 0) and (not(line_index % 2 == 0))) or ((pass_counter == 1) and (line_index % 2 == 0))):
                    # Calculate Y position of the line
                    y_position = squares_min_y + line_index*current_line_spacing + (row)*(square_size + square_spacing) + current_line_spacing
                    # Move to Line Start
                    move_to(squares_max_x, y_position)
                    # Scan each column within the line
                    for col in range(3):
                        # Get the starting x-coordinates of the square
                        start_x = squares_max_x - (col)*(square_size + square_spacing) # - current_line_spacing*0.3
                        # Move to start of line
                        move_to(start_x, y_position)
                        
                        end_x = start_x - square_size # + current_line_spacing*0.3
                        # Get the scan speed for the current column
                        current_scan_speed = scan_speeds[col % len(scan_speeds)]
                        scan_time_sec = scan_time_sec + 20/current_scan_speed                
                        laser_move_to(end_x, y_position, current_scan_speed)

    # Finishing Statements
    gcode.append("G0 X0 Y330 Z5")
    gcode.append("G28 X0 Y0 Z0")
    gcode.append("RECOATER_PULL")

    # Write the GCode to a file
    with open(filename, 'w') as file:
        file.write("\n".join(gcode))

    scan_time_mins = scan_time_sec/60
    return scan_time_mins

def main():
    # Prompt for scan speeds and line spacings
    scan_speeds = []
    line_spacings = []
    speed_labels = ['A', 'B', 'C']
    print("Enter 3 different scan speeds (in mm/s):")
    for label in speed_labels:
        speed = float(input(f"Scan speed {label}: "))
        scan_speeds.append(speed)

    print("Enter 3 different line spacings (in mm):")
    for i in range(3):
        spacing = float(input(f"Line spacing {i+1}: "))
        line_spacings.append(spacing)

    # Create a temporary filename based on the inputs
    temp_filename = f"squares_speedsABC_{'_'.join(map(str, scan_speeds))}_spacings123_{'_'.join(map(str, line_spacings))}.gcode"
    temp_filename = temp_filename.replace('.', 'p')  # Replace all dots with 'p' to avoid issues in filenames

    # Convert the last 'p' back to a dot
    temp_filename = temp_filename[::-1].replace('p', '.', 1)[::-1]

    scan_time_mins = generate_gcode(scan_speeds, line_spacings, temp_filename)
    print(f"GCode written to {temp_filename}")
    print(f"Total Scan Time: {scan_time_mins} mins")

    # Create the final filename including the total travel length
    final_filename = f"squares_with_OL_speedsABC_{'_'.join(map(str, scan_speeds))}_spacings123_{'_'.join(map(str, line_spacings))}_time_mins_{scan_time_mins:.2f}.gcode"
    final_filename = final_filename.replace('.', 'p')  # Replace all dots with 'p' to avoid issues in filenames

    # Convert the last 'p' back to a dot
    final_filename = final_filename[::-1].replace('p', '.', 1)[::-1]

    # Rename the temporary file to the final filename
    os.rename(temp_filename, final_filename)
    print(f"File renamed to {final_filename}")

if __name__ == "__main__":
    main()
