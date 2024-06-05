import os
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cv2

def generate_gcode(scan_speeds, line_spacings, filename):
    gcode = []
    scan_time_sec = 0.0
    pass_counter = 1

    # Squares parameters
    square_size = 20
    square_spacing = 5
    squares_max_x = 100
    squares_min_y = 260

    # Function to move to a point with laser off
    def move_to(x, y):
        gcode.append("M5 ; Laser Off")
        gcode.append(f"G0 X{x:.2f} Y{y:.2f} F3000")

    # Function to move to a point with laser on
    def laser_move_to(x, y, speed, start_dwell_ms, end_dwell_ms, keep_laser_on:bool):
        gcode.append("M3 S255 ; Laser On")
        if start_dwell_ms > 0:
            gcode.append(f"G4 P{start_dwell_ms}")
        gcode.append(f"G1 X{x:.2f} Y{y:.2f} F{speed*60:.2f}")
        if end_dwell_ms > 0:
            gcode.append(f"G4 P{end_dwell_ms}")
        if not(keep_laser_on):
            gcode.append("M5 ; Laser Off")
             
    def laser_move_to_with_stitches(start_x, start_y, final_x, final_y, stitch_length, speed):
        move_length = math.sqrt((final_x-start_x)**2+(final_y-start_y)**2)
        move_x_component = final_x - start_x
        move_y_component = final_y - start_y
        x_dir = move_x_component / move_length
        y_dir = move_y_component / move_length
        stitch_move_x = x_dir*stitch_length
        stitch_move_y = y_dir*stitch_length
        # Scan to start
        laser_move_to(x=start_x, 
                      y=start_y, 
                      speed=1, 
                      start_dwell_ms=0, 
                      end_dwell_ms=1500, 
                      keep_laser_on=True)
        # Scan past start
        laser_move_to(x=start_x + stitch_move_x, 
                      y=start_y + stitch_move_y, 
                      speed=1, start_dwell_ms=0, 
                      end_dwell_ms=0, 
                      keep_laser_on=True)
        # Scan to start
        laser_move_to(x=start_x, 
                      y=start_y, 
                      speed=0.5, 
                      start_dwell_ms=0, 
                      end_dwell_ms=0, 
                      keep_laser_on=True)
        # Scan to before end
        laser_move_to(x=final_x+1, 
                      y=final_y, 
                      speed=speed, 
                      start_dwell_ms=0, 
                      end_dwell_ms=0, 
                      keep_laser_on=True)
        # Scan to end
        laser_move_to(x=final_x, 
                      y=final_y, 
                      speed=0.5, 
                      start_dwell_ms=0, 
                      end_dwell_ms=500, 
                      keep_laser_on=True)

    def make_square(start_x, start_y, square_size):
        move_to(start_x, start_y)
        x_speed = 3
        y_speed = 0.5
        connector_trace_x = -0.5
        connector_trace_y = -0.5
        laser_move_to(x=start_x - square_size, 
                      y=start_y, speed=x_speed, 
                      start_dwell_ms=1500, 
                      end_dwell_ms=1500, 
                      keep_laser_on=False)
        laser_move_to(x=start_x - square_size, 
                      y=start_y + square_size, 
                      speed=y_speed, 
                      start_dwell_ms=1500, 
                      end_dwell_ms=1500, 
                      keep_laser_on=False)
        laser_move_to(x=start_x, 
                      y=start_y + square_size, 
                      speed=x_speed, 
                      start_dwell_ms=1500, 
                      end_dwell_ms=1500, 
                      keep_laser_on=False)
        laser_move_to(x=start_x, 
                      y=start_y, 
                      speed=y_speed, 
                      start_dwell_ms=1500, 
                      end_dwell_ms=0, 
                      keep_laser_on=True)
        laser_move_to_with_stitches(start_x=start_x, 
                                    start_y=start_y, 
                                    final_x=start_x + connector_trace_x, final_y=start_y + connector_trace_y,
                                    stitch_length=1,
                                    speed=y_speed)

    # Initialize the GCode
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Use absolute positioning")
    gcode.append("G28 X0 Y0 Z0")
    gcode.append("RECOATER_PUSH")
    gcode.append("RECOATER_PULL")



    # Generate GCode for each row of squares
    for row in range(3):
        # Get the line spacing for the current row of squares
        current_line_spacing = line_spacings[row % len(line_spacings)]
        # Calculate the number of lines to scan within each square
        num_lines = int((square_size - (2*(0.7*current_line_spacing))) / current_line_spacing)

        # First Column of Row Outline
        make_square(squares_max_x, 
                    squares_min_y + row*(square_size+square_spacing), 
                    square_size)
        # Second Column of Row Outline
        make_square(squares_max_x - square_size - square_spacing, 
                    squares_min_y + row*(square_size+square_spacing), 
                    square_size)
        # Third Column of Row Outline
        make_square(squares_max_x - 2*square_size - 2*square_spacing, 
                    squares_min_y + row*(square_size+square_spacing), 
                    square_size)
        for pass_counter in range(2):
            # For each line within the row
            speed_factor = 1.0 # Speed Factor for interlacing
            if pass_counter == 1: # If on the second pass, move slower
                speed_factor = 0.8
            for line_index in range(num_lines):
                if ((pass_counter == 0) and (not(line_index % 2 == 0))) or ((pass_counter == 1) and (line_index % 2 == 0)):
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
                        scan_time_sec = scan_time_sec + 20/(current_scan_speed*speed_factor)                
                        laser_move_to_with_stitches(start_x=start_x,
                                                    start_y=y_position,
                                                    final_x=end_x, final_y=y_position,
                                                    stitch_length=current_line_spacing,
                                                    speed=current_scan_speed*speed_factor)        
    # Finishing Statements
    gcode.append("G0 X0 Y330 Z5")
    gcode.append("G28 X0 Y0 Z0")
    gcode.append("RECOATER_PULL")
    # Write the GCode to a file
    with open(filename, 'w') as file:
        file.write("\n".join(gcode))

    scan_time_mins = scan_time_sec/60
    return scan_time_mins

def generate_image_from_gcode(gcode_file, image_file):
    coordinates_g0 = []
    coordinates_g1 = []
    feed_speeds = []
    current_position = (0, 0)
    current_speed = None
    
    with open(gcode_file, 'r') as f:
        for line in f:
            if line.startswith('G0') or line.startswith('G1'):
                parts = line.split()
                x = current_position[0]
                y = current_position[1]
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                    elif part.startswith('F'):
                        current_speed = float(part[1:])
                if line.startswith('G0'):
                    coordinates_g0.append((current_position, (x, y)))
                elif line.startswith('G1'):
                    coordinates_g1.append((current_position, (x, y), current_speed))
                    if current_speed is not None:
                        feed_speeds.append(current_speed)
                current_position = (x, y)

    # Normalize feed speeds for color mapping
    if feed_speeds:
        norm = plt.Normalize(min(feed_speeds), max(feed_speeds))
        cmap = plt.get_cmap('Reds_r')  # Reversed colormap
    
    plt.figure(figsize=(10, 10))
    
    labels_added = set()

    # Plot G0 lines in light gray dashes
    for start, end in coordinates_g0:
        label = 'G0' if 'G0' not in labels_added else ""
        plt.plot([start[0], end[0]], [start[1], end[1]], color='lightgray', linestyle='--', label=label)
        labels_added.add('G0')

    # Plot G1 lines with color gradient based on feed speed
    for start, end, speed in coordinates_g1:
        color = cmap(norm(speed)) if speed is not None else 'red'
        label = 'G1' if 'G1' not in labels_added else ""
        plt.plot([start[0], end[0]], [start[1], end[1]], color=color, linestyle='-', label=label)
        labels_added.add('G1')
    
    plt.title('G-code Path in XY Plane')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.xlim(110, 20)  # Set X-axis limits from 150 to 0
    plt.ylim(250, 340)  # Set Y-axis limits from 150 to 300
    
    # Add color bar to indicate feed speeds
    if feed_speeds:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, orientation='vertical', pad=0.1, fraction=0.046, aspect=30)
        cbar.set_label('Feed Speed (F)')
    
    # Add legend only if labels are present, and place it outside the plot
    handles, labels = plt.gca().get_legend_handles_labels()
    if labels:
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    plt.tight_layout()
    plt.savefig(image_file, bbox_inches='tight')
    plt.close()

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
    final_gcode_filename = f"squares_with_OL_speedsABC_{'_'.join(map(str, scan_speeds))}_spacings123_{'_'.join(map(str, line_spacings))}_time_mins_{scan_time_mins:.2f}.gcode"
    final_gcode_filename = final_gcode_filename.replace('.', 'p')  # Replace all dots with 'p' to avoid issues in filenames

    # Convert the last 'p' back to a dot
    final_gcode_filename = final_gcode_filename[::-1].replace('p', '.', 1)[::-1]

    # Rename the temporary file to the final filename
    os.rename(temp_filename, final_gcode_filename)
    print(f"File renamed to {final_gcode_filename}")

    image_file_name = final_gcode_filename.replace('.gcode', '.png')
    generate_image_from_gcode(final_gcode_filename, image_file_name)

if __name__ == "__main__":
    main()
