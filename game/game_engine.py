
import random
import pygame
from game.text_box import TextBox


class GameEngine:
    MAX_ATTEMPTS = 10

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)
        self.font_btn = pygame.font.SysFont(None, 26)

        self.reset()

    def reset(self):
        self.secret_number = random.randint(1, 100)
        self.attempts = 0

        self.min_range = 1
        self.max_range = 100

        self.history = []
        self.game_won = False
        self.game_over = False

        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)

        self.input_box.clear()

    def submit_guess(self):
        # Do not accept guesses after the game ends.
        if self.game_won or self.game_over:
            return

        # Fix 1: Handle empty input safely.
        text = self.input_box.text.strip()

        if not text:
            self.feedback_msg = "Please enter a number!"
            self.feedback_color = (240, 100, 80)
            return

        # Fix 2: Validate the input.
        try:
            guess = int(text)
        except ValueError:
            self.feedback_msg = "Please enter a valid integer!"
            self.feedback_color = (240, 100, 80)
            return

        if not 1 <= guess <= 100:
            self.feedback_msg = "Enter a number from 1 to 100!"
            self.feedback_color = (240, 100, 80)
            self.input_box.clear()
            return

        # Count only valid guesses.
        self.attempts += 1
        self.input_box.clear()

        if guess < self.secret_number:
            result = "TOO LOW"
            self.feedback_msg = f"TOO LOW! Guess: {guess}"
            self.feedback_color = (80, 160, 240)

            # Narrow the possible search range.
            self.min_range = max(self.min_range, guess + 1)

        elif guess > self.secret_number:
            result = "TOO HIGH"
            self.feedback_msg = f"TOO HIGH! Guess: {guess}"
            self.feedback_color = (240, 100, 80)

            self.max_range = min(self.max_range, guess - 1)

        else:
            result = "CORRECT"
            self.feedback_msg = (
                f"CORRECT! Found in {self.attempts} attempts."
            )
            self.feedback_color = (80, 220, 90)
            self.game_won = True

        # Fix 3: Save recent guesses for the history panel.
        self.history.append((guess, result))

        # Fix 4: End the game after the attempt limit.
        if not self.game_won and self.attempts >= self.MAX_ATTEMPTS:
            self.game_over = True
            self.feedback_msg = (
                f"GAME OVER! The number was {self.secret_number}."
            )
            self.feedback_color = (255, 90, 90)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        # Allow restarting after either winning or losing.
        if event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_r
                and (self.game_won or self.game_over)
            ):
                self.reset()
                return

        if self.game_won or self.game_over:
            return

        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.submit_btn.collidepoint(event.pos):
                    self.submit_guess()

    def update(self):
        pass

    def draw_centered(self, screen, text, font, color, y):
        surface = font.render(text, True, color)
        x = (self.width - surface.get_width()) // 2
        screen.blit(surface, (x, y))

    def render(self, screen):
        screen.fill((30, 34, 42))

        self.draw_centered(
            screen,
            "Number Guessing Arena",
            self.font_title,
            (245, 245, 245),
            30,
        )

        self.draw_centered(
            screen,
            f"Attempts: {self.attempts}/{self.MAX_ATTEMPTS}",
            self.font_medium,
            (180, 185, 195),
            80,
        )

        self.draw_centered(
            screen,
            f"Possible range: {self.min_range} - {self.max_range}",
            self.font_medium,
            (255, 220, 80),
            112,
        )

        self.input_box.render(screen)

        # Disable the button visually after the game ends.
        button_color = (
            (100, 100, 100)
            if self.game_won or self.game_over
            else (50, 150, 80)
        )

        pygame.draw.rect(
            screen, button_color, self.submit_btn, border_radius=6
        )
        pygame.draw.rect(
            screen, (220, 220, 220),
            self.submit_btn, width=2, border_radius=6
        )

        btn_text = self.font_btn.render(
            "SUBMIT", True, (255, 255, 255)
        )
        screen.blit(
            btn_text,
            (
                self.submit_btn.centerx - btn_text.get_width() // 2,
                self.submit_btn.centery - btn_text.get_height() // 2,
            ),
        )

        self.draw_centered(
            screen,
            self.feedback_msg,
            self.font_small,
            self.feedback_color,
            215,
        )

        # Recent guess history.
        self.draw_centered(
            screen,
            "Recent Guesses",
            self.font_medium,
            (245, 245, 245),
            255,
        )

        recent_guesses = self.history[-3:]

        if not recent_guesses:
            self.draw_centered(
                screen,
                "No guesses yet",
                self.font_small,
                (170, 175, 185),
                282,
            )
        else:
            for index, (guess, result) in enumerate(recent_guesses):
                if result == "TOO LOW":
                    color = (80, 160, 240)
                    indicator = "LOW"
                elif result == "TOO HIGH":
                    color = (240, 100, 80)
                    indicator = "HIGH"
                else:
                    color = (80, 220, 90)
                    indicator = "CORRECT"

                self.draw_centered(
                    screen,
                    f"{guess} - {indicator}",
                    self.font_small,
                    color,
                    282 + index * 22,
                )

        if self.game_won or self.game_over:
            self.draw_centered(
                screen,
                "Press R to start a new game",
                self.font_small,
                (255, 220, 80),
                self.height - 25,
            )
