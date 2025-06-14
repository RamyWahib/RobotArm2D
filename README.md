# 2D Robotic Arm Simulator

A Python-based 2D robotic arm simulator that demonstrates forward kinematics and real-time physics visualization.

## Features

- Interactive 2D robotic arm simulation
- Real-time forward kinematics calculations
- Adjustable segment lengths and joint angles
- Visual workspace representation
- End effector position tracking
- Physics-based arm movement

## Requirements

- Python 3.7+
- Pygame 2.5.2+
- NumPy 1.24.3+

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the simulator:

```bash
python robot_arm_simulator.py
```

## Controls

- **Segment Length Sliders**: Adjust the length of each arm segment (20-150 units)
- **Joint Angle Sliders**: Control the angle of each joint (-180° to +180°)
- **Real-time Updates**: The arm updates immediately as you adjust the controls

## Features Explained

### Forward Kinematics
The simulator calculates the position of each joint and the end effector using forward kinematics equations:
- Each joint's position is calculated based on the cumulative angle and segment lengths
- The end effector position is displayed in real-time

### Workspace Visualization
- A circle shows the maximum reach of the robotic arm
- The workspace area is calculated and displayed
- Joint positions are highlighted with red circles
- The end effector is shown as a green circle

### Interactive Controls
- Drag sliders to adjust parameters in real-time
- Visual feedback shows current values
- Smooth animation updates

## Technical Details

- Built with Pygame for graphics and user interaction
- Uses trigonometric calculations for accurate kinematics
- Implements a clean object-oriented design
- Real-time rendering at 60 FPS

## Customization

You can easily modify the simulator by:
- Changing the number of segments in the `initial_segments` list
- Adjusting the slider ranges for different arm configurations
- Modifying colors and visual appearance
- Adding inverse kinematics functionality

Enjoy experimenting with different robotic arm configurations!
