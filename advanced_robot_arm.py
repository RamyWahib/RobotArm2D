import pygame
import math
import numpy as np
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1400
HEIGHT = 900
FPS = 60
BG_COLOR = (15, 20, 35)
ARM_COLOR = (70, 130, 255)
JOINT_COLOR = (255, 80, 80)
END_EFFECTOR_COLOR = (80, 255, 80)
TEXT_COLOR = (255, 255, 255)
PANEL_COLOR = (30, 35, 50)
TRACE_COLOR = (255, 255, 100)


class AdvancedRobotArm:
    def __init__(self, segments: List[float], angles: List[float]):
        self.segments = segments
        self.angles = angles
        self.base_pos = (WIDTH // 2 + 100, HEIGHT // 2)
        self.joint_positions = []
        self.end_effector_pos = (0, 0)
        self.trace_points = []
        self.max_trace_points = 500
        self.joint_velocities = [0.0] * len(angles)
        self.calculate_positions()

    def calculate_positions(self):
        """Calculate forward kinematics with improved precision"""
        self.joint_positions = [self.base_pos]
        current_x, current_y = self.base_pos
        cumulative_angle = 0

        for i, (length, angle) in enumerate(zip(self.segments, self.angles)):
            cumulative_angle += math.radians(angle)
            next_x = current_x + length * math.cos(cumulative_angle)
            next_y = current_y + length * math.sin(cumulative_angle)
            self.joint_positions.append((next_x, next_y))
            current_x, current_y = next_x, next_y

        # Update end effector and trace
        old_pos = self.end_effector_pos
        self.end_effector_pos = (current_x, current_y)

        # Add to trace if position changed significantly
        if len(self.trace_points) == 0 or \
                math.sqrt((current_x - old_pos[0]) ** 2 + (current_y - old_pos[1]) ** 2) > 2:
            self.trace_points.append((current_x, current_y))
            if len(self.trace_points) > self.max_trace_points:
                self.trace_points.pop(0)

    def update_angles(self, angles: List[float]):
        old_angles = self.angles.copy()
        self.angles = angles
        # Calculate velocities
        for i in range(len(angles)):
            self.joint_velocities[i] = angles[i] - old_angles[i]
        self.calculate_positions()

    def update_segments(self, segments: List[float]):
        self.segments = segments
        self.calculate_positions()

    def get_reach(self) -> float:
        return sum(self.segments)

    def get_min_reach(self) -> float:
        if len(self.segments) <= 1:
            return 0
        return abs(max(self.segments) - sum(
            s for i, s in enumerate(self.segments) if i != self.segments.index(max(self.segments))))

    def get_workspace_area(self) -> float:
        max_reach = self.get_reach()
        min_reach = self.get_min_reach()
        return math.pi * (max_reach ** 2 - min_reach ** 2)

    def clear_trace(self):
        self.trace_points = []

    def get_joint_info(self, joint_idx: int) -> dict:
        if joint_idx < len(self.joint_positions):
            return {
                'position': self.joint_positions[joint_idx],
                'angle': self.angles[joint_idx] if joint_idx < len(self.angles) else 0,
                'velocity': self.joint_velocities[joint_idx] if joint_idx < len(self.joint_velocities) else 0
            }
        return {}


class AdvancedSlider:
    def __init__(self, x: int, y: int, w: int, h: int, min_val: float, max_val: float, initial_val: float, label: str,
                 precision: int = 1):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.precision = precision
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        handle_x = self.rect.x + int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width) - 6
        self.handle_rect = pygame.Rect(handle_x, self.rect.y - 3, 12, self.rect.height + 6)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_from_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_from_mouse(event.pos)

    def update_from_mouse(self, pos):
        rel_x = pos[0] - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))
        self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
        self.val = round(self.val, self.precision)
        self.update_handle_pos()

    def draw(self, screen, font):
        # Draw slider track
        pygame.draw.rect(screen, (50, 50, 50), self.rect, border_radius=3)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2, border_radius=3)

        # Draw handle
        pygame.draw.rect(screen, (120, 120, 120), self.handle_rect, border_radius=6)
        pygame.draw.rect(screen, (160, 160, 160), self.handle_rect, 2, border_radius=6)

        # Draw label and value
        label_text = font.render(f"{self.label}: {self.val:.{self.precision}f}", True, TEXT_COLOR)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Advanced 2D Robotic Arm Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)
    title_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 18)

    # Initialize robot arm with more segments
    initial_segments = [120, 100, 80, 60]
    initial_angles = [0, 0, 0, 0]
    robot_arm = AdvancedRobotArm(initial_segments, initial_angles)

    # Create sliders
    sliders = []
    num_segments = len(initial_segments)

    # Segment length sliders
    for i in range(num_segments):
        slider = AdvancedSlider(50, 80 + i * 50, 220, 18, 20, 200, initial_segments[i], f"Segment {i + 1} Length")
        sliders.append(slider)

    # Angle sliders
    for i in range(num_segments):
        slider = AdvancedSlider(50, 300 + i * 50, 220, 18, -180, 180, initial_angles[i], f"Joint {i + 1} Angle")
        sliders.append(slider)

    # Control buttons
    clear_trace_button = pygame.Rect(50, 550, 100, 30)
    show_trace = True
    show_workspace = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if clear_trace_button.collidepoint(event.pos):
                    robot_arm.clear_trace()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    show_trace = not show_trace
                elif event.key == pygame.K_w:
                    show_workspace = not show_workspace
                elif event.key == pygame.K_c:
                    robot_arm.clear_trace()

            for slider in sliders:
                slider.handle_event(event)

        # Update robot arm
        segments = [sliders[i].val for i in range(num_segments)]
        angles = [sliders[i].val for i in range(num_segments, num_segments * 2)]
        robot_arm.update_segments(segments)
        robot_arm.update_angles(angles)

        # Clear screen with gradient effect
        screen.fill(BG_COLOR)

        # Draw control panel
        pygame.draw.rect(screen, PANEL_COLOR, (20, 20, 300, HEIGHT - 40), border_radius=10)
        pygame.draw.rect(screen, (60, 65, 80), (20, 20, 300, HEIGHT - 40), 2, border_radius=10)

        # Draw title
        title = title_font.render("Advanced Robot Arm", True, TEXT_COLOR)
        screen.blit(title, (30, 30))

        # Draw sliders
        for slider in sliders:
            slider.draw(screen, font)

        # Draw control buttons
        pygame.draw.rect(screen, (80, 80, 80), clear_trace_button, border_radius=5)
        pygame.draw.rect(screen, (120, 120, 120), clear_trace_button, 2, border_radius=5)
        clear_text = font.render("Clear Trace", True, TEXT_COLOR)
        screen.blit(clear_text, (clear_trace_button.x + 10, clear_trace_button.y + 8))

        # Draw info panel
        info_y = 600
        info_texts = [
            f"End Effector: ({robot_arm.end_effector_pos[0]:.1f}, {robot_arm.end_effector_pos[1]:.1f})",
            f"Max Reach: {robot_arm.get_reach():.1f}",
            f"Min Reach: {robot_arm.get_min_reach():.1f}",
            f"Workspace: {robot_arm.get_workspace_area():.0f} px²",
            f"Segments: {len(robot_arm.segments)}",
            f"Trace Points: {len(robot_arm.trace_points)}",
            "",
            "Controls:",
            "T - Toggle trace",
            "W - Toggle workspace",
            "C - Clear trace"
        ]

        for i, text in enumerate(info_texts):
            color = TEXT_COLOR if not text.startswith(("T -", "W -", "C -")) else (180, 180, 180)
            rendered = small_font.render(text, True, color)
            screen.blit(rendered, (30, info_y + i * 20))

        # Draw workspace circles
        if show_workspace:
            pygame.draw.circle(screen, (40, 40, 40), robot_arm.base_pos, int(robot_arm.get_reach()), 2)
            if robot_arm.get_min_reach() > 0:
                pygame.draw.circle(screen, (40, 40, 40), robot_arm.base_pos, int(robot_arm.get_min_reach()), 2)

        # Draw trace
        if show_trace and len(robot_arm.trace_points) > 1:
            for i in range(1, len(robot_arm.trace_points)):
                if i > 1:
                    pygame.draw.line(screen, TRACE_COLOR, robot_arm.trace_points[i - 1], robot_arm.trace_points[i], 2)

        # Draw robot arm segments
        for i in range(len(robot_arm.joint_positions) - 1):
            start_pos = robot_arm.joint_positions[i]
            end_pos = robot_arm.joint_positions[i + 1]
            pygame.draw.line(screen, ARM_COLOR, start_pos, end_pos, 12)
            pygame.draw.line(screen, (100, 160, 255), start_pos, end_pos, 8)

        # Draw joints
        for i, pos in enumerate(robot_arm.joint_positions):
            pygame.draw.circle(screen, JOINT_COLOR, (int(pos[0]), int(pos[1])), 10)
            pygame.draw.circle(screen, (255, 120, 120), (int(pos[0]), int(pos[1])), 8)

            # Draw joint numbers
            if i < len(robot_arm.angles):
                joint_text = small_font.render(str(i + 1), True, TEXT_COLOR)
                screen.blit(joint_text, (int(pos[0]) - 5, int(pos[1]) - 20))

        # Draw end effector
        pygame.draw.circle(screen, END_EFFECTOR_COLOR,
                           (int(robot_arm.end_effector_pos[0]), int(robot_arm.end_effector_pos[1])), 15)
        pygame.draw.circle(screen, (120, 255, 120),
                           (int(robot_arm.end_effector_pos[0]), int(robot_arm.end_effector_pos[1])), 12)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
