"""
THE LAST HOUR - PROJECT ECHO
Mobile Touch Controls & Virtual On-Screen Joystick Subsystem.
Supports both native Android multi-touch (Raylib get_touch_*) and PC mouse simulation.
"""
import math
from pyray import (
    Vector2, Color, WHITE, BLACK,
    get_touch_point_count, get_touch_position, get_touch_point_id,
    get_mouse_position, is_mouse_button_down, is_mouse_button_pressed,
    draw_circle, draw_circle_lines, draw_line, draw_text, measure_text,
    MOUSE_BUTTON_LEFT
)

class MobileTouchController:
    def __init__(self, screen_w=1366, screen_h=768):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        # Virtual Joystick (bottom-left)
        self.joy_center_x = 150.0
        self.joy_center_y = screen_h - 150.0
        self.joy_radius = 70.0
        self.knob_radius = 30.0
        self.joy_knob_x = self.joy_center_x
        self.joy_knob_y = self.joy_center_y
        self.joy_active = False
        self.joy_touch_id = -1
        self.joy_val_x = 0.0  # -1.0 (left) to +1.0 (right)
        self.joy_val_y = 0.0  # -1.0 (back) to +1.0 (forward)
        
        # Touch Camera Swipe Look (right half of screen)
        self.look_touch_id = -1
        self.look_last_x = 0.0
        self.look_last_y = 0.0
        self.look_delta_x = 0.0
        self.look_delta_y = 0.0
        self.look_sensitivity = 0.0035
        
        # Action Buttons (right side)
        # Button USE [E]
        self.btn_use_x = screen_w - 110.0
        self.btn_use_y = screen_h - 130.0
        self.btn_use_r = 46.0
        self.btn_use_pressed = False
        
        # Button LIGHT [F]
        self.btn_light_x = screen_w - 110.0
        self.btn_light_y = screen_h - 245.0
        self.btn_light_r = 34.0
        self.btn_light_pressed = False
        
        # Button SPRINT [RUN]
        self.btn_run_x = screen_w - 215.0
        self.btn_run_y = screen_h - 130.0
        self.btn_run_r = 34.0
        self.btn_run_toggle = False
        self.btn_run_pressed = False
        
        # Button JUMP [SPACE]
        self.btn_jump_x = screen_w - 215.0
        self.btn_jump_y = screen_h - 225.0
        self.btn_jump_r = 32.0
        self.btn_jump_pressed = False
        
        # Button MENU [ESC] (top-left)
        self.btn_menu_x = 48.0
        self.btn_menu_y = 48.0
        self.btn_menu_r = 24.0
        self.btn_menu_pressed = False
        
        # Active tracked button touch IDs to prevent double trigger
        self._down_touch_ids = set()
        self.is_mobile_mode = True

    def update(self):
        self.btn_use_pressed = False
        self.btn_light_pressed = False
        self.btn_jump_pressed = False
        self.btn_menu_pressed = False
        self.look_delta_x = 0.0
        self.look_delta_y = 0.0
        
        # Collect active touch points
        touch_count = get_touch_point_count()
        touches = []
        if touch_count > 0:
            for i in range(touch_count):
                pos = get_touch_position(i)
                tid = get_touch_point_id(i)
                touches.append((tid, float(pos.x), float(pos.y)))
        else:
            # Fallback to mouse on PC (allows testing virtual controls with mouse)
            if is_mouse_button_down(MOUSE_BUTTON_LEFT):
                mpos = get_mouse_position()
                touches.append((999, float(mpos.x), float(mpos.y)))
                
        active_tids = {t[0] for t in touches}
        
        # Remove ended touches from tracking set
        self._down_touch_ids = {tid for tid in self._down_touch_ids if tid in active_tids}
        
        # Reset joystick if its touch point ended
        if self.joy_touch_id not in active_tids:
            self.joy_active = False
            self.joy_touch_id = -1
            self.joy_knob_x = self.joy_center_x
            self.joy_knob_y = self.joy_center_y
            self.joy_val_x = 0.0
            self.joy_val_y = 0.0
            
        # Reset swipe look if its touch point ended
        if self.look_touch_id not in active_tids:
            self.look_touch_id = -1

        # Process each active touch
        for tid, tx, ty in touches:
            is_new_touch = (tid not in self._down_touch_ids)
            
            # Check Button: USE [E]
            if math.hypot(tx - self.btn_use_x, ty - self.btn_use_y) <= self.btn_use_r:
                if is_new_touch:
                    self.btn_use_pressed = True
                    self._down_touch_ids.add(tid)
                continue
                
            # Check Button: LIGHT [F]
            if math.hypot(tx - self.btn_light_x, ty - self.btn_light_y) <= self.btn_light_r:
                if is_new_touch:
                    self.btn_light_pressed = True
                    self._down_touch_ids.add(tid)
                continue
                
            # Check Button: RUN
            if math.hypot(tx - self.btn_run_x, ty - self.btn_run_y) <= self.btn_run_r:
                if is_new_touch:
                    self.btn_run_toggle = not self.btn_run_toggle
                    self.btn_run_pressed = True
                    self._down_touch_ids.add(tid)
                continue
                
            # Check Button: JUMP
            if math.hypot(tx - self.btn_jump_x, ty - self.btn_jump_y) <= self.btn_jump_r:
                if is_new_touch:
                    self.btn_jump_pressed = True
                    self._down_touch_ids.add(tid)
                continue
                
            # Check Button: MENU [ESC]
            if math.hypot(tx - self.btn_menu_x, ty - self.btn_menu_y) <= self.btn_menu_r:
                if is_new_touch:
                    self.btn_menu_pressed = True
                    self._down_touch_ids.add(tid)
                continue

            # Check Virtual Joystick (bottom-left quadrant)
            if tx < self.screen_w * 0.45 and ty > self.screen_h * 0.35:
                if not self.joy_active and is_new_touch:
                    self.joy_active = True
                    self.joy_touch_id = tid
                    self._down_touch_ids.add(tid)
                    
                if self.joy_touch_id == tid:
                    dx = tx - self.joy_center_x
                    dy = ty - self.joy_center_y
                    dist = math.hypot(dx, dy)
                    if dist > self.joy_radius:
                        dx = (dx / dist) * self.joy_radius
                        dy = (dy / dist) * self.joy_radius
                    self.joy_knob_x = self.joy_center_x + dx
                    self.joy_knob_y = self.joy_center_y + dy
                    self.joy_val_x = dx / self.joy_radius
                    # Screen Y is inverted (dragging UP is negative Y, meaning forward)
                    self.joy_val_y = -dy / self.joy_radius
                continue

            # Check Swipe Look (right half of screen, avoiding buttons)
            if tx >= self.screen_w * 0.45:
                if self.look_touch_id == -1 and is_new_touch:
                    self.look_touch_id = tid
                    self.look_last_x = tx
                    self.look_last_y = ty
                    self._down_touch_ids.add(tid)
                elif self.look_touch_id == tid:
                    self.look_delta_x = tx - self.look_last_x
                    self.look_delta_y = ty - self.look_last_y
                    self.look_last_x = tx
                    self.look_last_y = ty
                continue

    def draw(self, hovered_object=None, torch_active=False):
        if not self.is_mobile_mode:
            return
            
        # 1. Draw Virtual Joystick
        draw_circle(int(self.joy_center_x), int(self.joy_center_y), self.joy_radius, Color(12, 22, 32, 130))
        draw_circle_lines(int(self.joy_center_x), int(self.joy_center_y), self.joy_radius, Color(0, 220, 255, 160))
        draw_line(int(self.joy_center_x - self.joy_radius + 8), int(self.joy_center_y),
                  int(self.joy_center_x + self.joy_radius - 8), int(self.joy_center_y), Color(0, 180, 220, 70))
        draw_line(int(self.joy_center_x), int(self.joy_center_y - self.joy_radius + 8),
                  int(self.joy_center_x), int(self.joy_center_y + self.joy_radius - 8), Color(0, 180, 220, 70))
        
        knob_color = Color(0, 240, 255, 220) if self.joy_active else Color(0, 180, 220, 150)
        draw_circle(int(self.joy_knob_x), int(self.joy_knob_y), self.knob_radius, knob_color)
        draw_circle_lines(int(self.joy_knob_x), int(self.joy_knob_y), self.knob_radius, Color(220, 250, 255, 240))
        
        # 2. Draw Button USE [E]
        is_interactive = (hovered_object is not None)
        use_bg = Color(245, 160, 30, 210) if is_interactive else Color(12, 22, 32, 130)
        use_border = Color(255, 210, 60, 255) if is_interactive else Color(0, 220, 255, 160)
        draw_circle(int(self.btn_use_x), int(self.btn_use_y), self.btn_use_r, use_bg)
        draw_circle_lines(int(self.btn_use_x), int(self.btn_use_y), self.btn_use_r, use_border)
        use_txt = "USE" if not is_interactive else "ACT"
        txt_w = measure_text(use_txt, 16)
        draw_text(use_txt, int(self.btn_use_x - txt_w // 2), int(self.btn_use_y - 8), 16, WHITE)
        
        # 3. Draw Button LIGHT [F]
        light_bg = Color(255, 220, 80, 200) if torch_active else Color(12, 22, 32, 130)
        light_border = Color(255, 240, 120, 255) if torch_active else Color(0, 220, 255, 140)
        draw_circle(int(self.btn_light_x), int(self.btn_light_y), self.btn_light_r, light_bg)
        draw_circle_lines(int(self.btn_light_x), int(self.btn_light_y), self.btn_light_r, light_border)
        light_txt = "LIGHT"
        lt_w = measure_text(light_txt, 14)
        draw_text(light_txt, int(self.btn_light_x - lt_w // 2), int(self.btn_light_y - 7), 14, WHITE if not torch_active else BLACK)
        
        # 4. Draw Button RUN
        run_bg = Color(0, 220, 150, 190) if self.btn_run_toggle else Color(12, 22, 32, 130)
        draw_circle(int(self.btn_run_x), int(self.btn_run_y), self.btn_run_r, run_bg)
        draw_circle_lines(int(self.btn_run_x), int(self.btn_run_y), self.btn_run_r, Color(0, 220, 255, 140))
        run_txt = "RUN"
        rn_w = measure_text(run_txt, 14)
        draw_text(run_txt, int(self.btn_run_x - rn_w // 2), int(self.btn_run_y - 7), 14, WHITE)
        
        # 5. Draw Button JUMP
        draw_circle(int(self.btn_jump_x), int(self.btn_jump_y), self.btn_jump_r, Color(12, 22, 32, 130))
        draw_circle_lines(int(self.btn_jump_x), int(self.btn_jump_y), self.btn_jump_r, Color(0, 220, 255, 140))
        jump_txt = "JUMP"
        jp_w = measure_text(jump_txt, 13)
        draw_text(jump_txt, int(self.btn_jump_x - jp_w // 2), int(self.btn_jump_y - 6), 13, WHITE)
        
        # 6. Draw Button MENU [ESC]
        draw_circle(int(self.btn_menu_x), int(self.btn_menu_y), self.btn_menu_r, Color(12, 22, 32, 160))
        draw_circle_lines(int(self.btn_menu_x), int(self.btn_menu_y), self.btn_menu_r, Color(0, 220, 255, 180))
        menu_txt = "ESC"
        mn_w = measure_text(menu_txt, 14)
        draw_text(menu_txt, int(self.btn_menu_x - mn_w // 2), int(self.btn_menu_y - 7), 14, WHITE)
