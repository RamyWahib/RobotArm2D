import pygame
import math
import numpy as np
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1200
HEIGHT = 800
FPS = 60
BG_COLOR = (20, 25, 40)
ARM_COLOR = (100, 150, 255)
JOINT_COLOR = (255, 100, 100)
END_EFFECTOR_COLOR = (100, 255, 100)
TEXT_COLOR = (255, 255, 255)
PANEL_COLOR = (40, 45, 60)


class RobotArm:
    def __init__(self, segments: List[float], angles: List[float]):
        self.segments = segments
        self.angles = angles
        self.base_pos = (WIDTH // 2, HEIGHT // 2)
        self.joint_positions = []
        self.end_effector_pos = (0, 0)
        self.calculate_positions()

    def calculate_positions(self):
        """Calculate forward kinematics"""
        self.joint_positions = [self.base_pos]
        current_x, current_y = self.base_pos
        cumulative_angle = 0

        for i, (length, angle) in enumerate(zip(self.segments, self.angles)):
            cumulative_angle += math.radians(angle)
            next_x = current_x + length * math.cos(cumulative_angle)
            next_y = current_y + length * math.sin(cumulative_angle)
            self.joint_positions.append((next_x, next_y))
            current_x, current_y = next_x, next_y

        self.end_effector_pos = (current_x, current_y)

    def update_angles(self, angles: List[float]):
        self.angles = angles
        self.calculate_positions()

    def update_segments(self, segments: List[float]):
        self.segments = segments
        self.calculate_positions()

    def get_reach(self) -> float:
        return sum(self.segments)

    def get_workspace_area(self) -> float:
        max_reach = sum(self.segments)
        min_reach = abs(max(self.segments) - sum(self.segments[:-1]))
        return math.pi * (max_reach ** 2 - min_reach ** 2)


class Slider:
    def __init__(self, x: int, y: int, w: int, h: int, min_val: float, max_val: float, initial_val: float, label: str):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.handle_rect = pygame.Rect(x + int((initial_val - min_val) / (max_val - min_val) * w) - 5, y - 2, 10, h + 4)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.handle_rect.x = self.rect.x + rel_x - 5

    def draw(self, screen, font):
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.handle_rect)
        label_text = font.render(f"{self.label}: {self.val:.1f}", True, TEXT_COLOR)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Robotic Arm Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)

    # Initialize robot arm
    initial_segments = [100, 80, 60]
    initial_angles = [0, 0, 0]
    robot_arm = RobotArm(initial_segments, initial_angles)

    # Create sliders
    sliders = []
    # Segment length sliders
    for i in range(3):
        slider = Slider(50, 100 + i * 60, 200, 20, 20, 150, initial_segments[i], f"Segment {i + 1} Length")
        sliders.append(slider)

    # Angle sliders
    for i in range(3):
        slider = Slider(50, 300 + i * 60, 200, 20, -180, 180, initial_angles[i], f"Joint {i + 1} Angle")
        sliders.append(slider)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for slider in sliders:
                slider.handle_event(event)

        # Update robot arm with slider values
        segments = [sliders[i].val for i in range(3)]
        angles = [sliders[i].val for i in range(3, 6)]
        robot_arm.update_segments(segments)
        robot_arm.update_angles(angles)

        # Clear screen
        screen.fill(BG_COLOR)

        # Draw control panel background
        pygame.draw.rect(screen, PANEL_COLOR, (20, 20, 280, HEIGHT - 40))

        # Draw title
        title = title_font.render("Robot Arm Simulator", True, TEXT_COLOR)
        screen.blit(title, (30, 30))

        # Draw sliders
        for slider in sliders:
            slider.draw(screen, font)

        # Draw info panel
        info_y = 500
        info_texts = [
            f"End Effector: ({robot_arm.end_effector_pos[0]:.1f}, {robot_arm.end_effector_pos[1]:.1f})",
            f"Max Reach: {robot_arm.get_reach():.1f}",
            f"Workspace Area: {robot_arm.get_workspace_area():.0f}",
            f"Total Segments: {len(robot_arm.segments)}"
        ]

        for i, text in enumerate(info_texts):
            rendered = font.render(text, True, TEXT_COLOR)
            screen.blit(rendered, (30, info_y + i * 25))

        # Draw robot arm
        for i in range(len(robot_arm.joint_positions) - 1):
            start_pos = robot_arm.joint_positions[i]
            end_pos = robot_arm.joint_positions[i + 1]
            pygame.draw.line(screen, ARM_COLOR, start_pos, end_pos, 8)

        # Draw joints
        for pos in robot_arm.joint_positions:
            pygame.draw.circle(screen, JOINT_COLOR, (int(pos[0]), int(pos[1])), 8)

        # Draw end effector
        pygame.draw.circle(screen, END_EFFECTOR_COLOR,
                           (int(robot_arm.end_effector_pos[0]), int(robot_arm.end_effector_pos[1])), 12)

        # Draw workspace circle (max reach)
        pygame.draw.circle(screen, (50, 50, 50), robot_arm.base_pos, int(robot_arm.get_reach()), 2)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
