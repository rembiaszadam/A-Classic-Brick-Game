import arcade
import arcade.gui
import random
import math
import time

# Paddle dimensions.
PADDLE_Y = 100
PADDLE_HEIGHT = 10
PADDLE_WIDTH = 50
PADDLE_HALF = PADDLE_WIDTH / 2

# Ball properties.
BALL_RADIUS = 5
BALL_DY = 4
MAX_BALL_ANGLE = math.radians(60)

# Set the height of the ball above the paddle after it is
# rebound to avoid additional hit detection due to resolution of ball position.
BOUNCE_HEIGHT = PADDLE_Y + (PADDLE_HEIGHT/2) + BALL_RADIUS

# Brick properties.
BRICK_WIDTH = 32
BRICK_HEIGHT = 8
# Maximum distances of the ball center to brick center when ball touches a brick.
BRICK_HIT_X = (BRICK_WIDTH / 2)
BRICK_HIT_Y = (BRICK_HEIGHT / 2)
# Wall shape/position
BRICK_COLUMNS = 14
BRICK_ROWS = 8
BRICK_GAP = 3
WALL_HEIGHT = 500   # Height of bottom row of bricks

# Screen properties.
SCREEN_WIDTH = ((BRICK_WIDTH + BRICK_GAP) * BRICK_COLUMNS) + BRICK_GAP
# SCREEN_WIDTH = 493
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Breakout"


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Create and enable the UIManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create sprite list variables.
        self.ball_list = None
        self.brick_list = None

        # Single constant sprite.
        self.paddle = arcade.SpriteSolidColor(PADDLE_WIDTH, PADDLE_HEIGHT, arcade.color.WHITE)
        self.paddle.position = SCREEN_WIDTH / 2, PADDLE_Y

        # Set max and min x positions of paddle to avoid going off of the screen.
        self.paddle_x_min = PADDLE_WIDTH / 2
        self.paddle_x_max = SCREEN_WIDTH - self.paddle_x_min

        # Create game variables.
        self.score = 0
        self.lives = 3
        self.round = 1

        # Set window background color.
        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        # Reset lives each round.
        self.lives = 3

        # Set sprite lists.
        self.ball_list = arcade.SpriteList()
        self.brick_list = arcade.SpriteList()

        # Build the wall.
        self.build_wall()

        # Create and set a ball.
        self.ball_reset()

    def on_update(self, delta_time: float):

        # Check ball interaction.
        for ball in self.ball_list:

            # Make ball bounce off of ceiling, left and right walls.
            if ball.top >= SCREEN_HEIGHT:
                ball.change_y *= -1
                # Avoid more than 1 interaction with ceiling.
                ball.center_y = SCREEN_HEIGHT - BALL_RADIUS
            elif ball.left <= 0:
                ball.change_x *= -1
                # Avoid more than 1 interaction with left wall.
                ball.center_x = BALL_RADIUS
            elif ball.right >= SCREEN_WIDTH:
                ball.change_x *= -1
                # Avoid more than 1 interaction with right wall.
                ball.center_x = SCREEN_WIDTH - BALL_RADIUS

            # When the ball falls below pad off of screen.
            elif ball.bottom <= 0:
                # Remove ball from sprite list and remove life.
                ball.remove_from_sprite_lists()
                self.lives -= 1
                # If user still has lives create new ball otherwise end game.
                if self.lives > 0:
                    self.ball_reset()
                else:
                    # Ask user if they want to play again.
                    message_box = arcade.gui.UIMessageBox(
                        width=230,
                        height=100,
                        message_text=(
                            "Would you like to play again?"
                        ),
                        buttons=["Yes", "Quit"],
                        callback=self.end_game
                    )

                    self.manager.add(message_box)

            # Ball bouncing off of paddle.
            if ball.collides_with_sprite(self.paddle):
                self.pad_return(ball)

            # Ball hitting bricks.
            hit_list = arcade.check_for_collision_with_list(ball, self.brick_list)
            if len(hit_list) > 0:
                self.brick_hit(hit_list[0], ball)

        self.paddle.update()
        self.ball_list.update()

    def on_draw(self):
        arcade.start_render()

        self.paddle.draw()
        self.brick_list.draw()
        self.ball_list.draw()
        self.manager.draw()

        # Show lives, score and round.
        arcade.draw_text(f" Score: {self.score}",
                         0,
                         SCREEN_HEIGHT - 30,
                         arcade.color.WHITE,
                         14,
                         width=SCREEN_WIDTH,
                         align="center")
        arcade.draw_text(f"Lives: {self.lives}",
                         10,
                         SCREEN_HEIGHT - 30,
                         arcade.color.WHITE,
                         14,
                         width=100,
                         align="left")
        arcade.draw_text(f"Round: {self.round} ",
                         SCREEN_WIDTH - 100 - 10,
                         SCREEN_HEIGHT - 30,
                         arcade.color.WHITE,
                         14,
                         width=100,
                         align="right")

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Tie the position of the paddle to the position of the
        cursor within paddle x limits."""
        if self.paddle_x_min < x < self.paddle_x_max:
            self.paddle.center_x = x
        elif x < self.paddle_x_min:
            self.paddle.center_x = self.paddle_x_min
        else:
            self.paddle.center_x = self.paddle_x_max

    def pad_return(self, ball):
        """Bounce the ball off of the paddle."""
        # After rebound from paddle set ball angle between 0 and MAX_BALL_ANGLE proportional
        # to distance from center of paddle.
        ball_angle = ((ball.center_x - self.paddle.center_x) / PADDLE_HALF) * MAX_BALL_ANGLE

        # Keep y-velocity constant.
        ball.change_y = BALL_DY
        # Set x-velocity based on ball angle and y-velocity.
        ball.change_x = BALL_DY * math.tan(ball_angle)

        # Set height of ball above pad to avoid additional contact.
        ball.center_y = BOUNCE_HEIGHT

    def brick_hit(self, brick, ball):
        """Determine which side of the brick was hit, how the ball is to
        rebound and remove brick from sprite list"""
        # Hitting the side of a brick.
        if (math.fabs(ball.center_y - brick.center_y) < BRICK_HIT_Y and
                math.fabs(ball.center_x - brick.center_x) > BRICK_HIT_X):
            ball.change_x *= -1
        # Hitting the top or bottom of a brick.
        elif (math.fabs(ball.center_x - brick.center_x) < BRICK_HIT_X and
              math.fabs(ball.center_y - brick.center_y) > BRICK_HIT_Y):
            ball.change_y *= -1

        # Set the direction of x and y velocity based on which corner is hit.
        else:
            # Left side of brick.
            if ball.center_x < brick.center_x:
                dx = -1
            # Right side of brick.
            else:
                dx = 1
            # Bottom of brick.
            if ball.center_y < brick.center_y:
                dy = -1
            # Top of brick
            else:
                dy = 1

            # Rebound the ball at 45°.
            ball.change_y = BALL_DY * dy
            ball.change_x = BALL_DY * dx

        # Remove brick from sprite list.
        brick.remove_from_sprite_lists()
        # Increase score after each brick is hit.
        self.score += 1

        # If all bricks are hit go to next round.
        if len(self.brick_list) == 0:
            self.round += 1
            self.setup()

    def ball_reset(self):
        """Set up the ball"""
        ball = arcade.SpriteCircle(BALL_RADIUS, arcade.color.WHITE)
        ball.position = self.paddle.center_x, PADDLE_Y + (PADDLE_HEIGHT / 2) + BALL_RADIUS
        time.sleep(1)
        # Set random x-directio for the ball.
        ball.change_x = random.choice([-3, -2, 3, 2])
        ball.change_y = BALL_DY
        # Add new ball to sprite list.
        self.ball_list.append(ball)

    def build_wall(self):
        """Build a new wall"""
        # Set brick colors to be used.
        brick_color = [arcade.color.YELLOW, arcade.color.GREEN, arcade.color.ORANGE, arcade.color.RED]
        color_index = 0

        # Build brick pattern based on defined number of rows and columns.
        for row in range(BRICK_ROWS):
            for column in range(BRICK_COLUMNS):
                brick = arcade.SpriteSolidColor(BRICK_WIDTH, BRICK_HEIGHT, brick_color[color_index])

                brick.center_x = (column * (BRICK_WIDTH + BRICK_GAP)) + ((BRICK_WIDTH / 2) + BRICK_GAP)
                brick.center_y = WALL_HEIGHT + ((BRICK_HEIGHT + BRICK_GAP) * row)

                # Add to sprite list.
                self.brick_list.append(brick)

            # If row number is even use next
            # color from list for next row.
            if (row + 1) % 2 == 0:
                color_index += 1

    def end_game(self, text):
        """Restart or quit game based on user choice."""
        if text == "Yes":
            self.setup()
        else:
            arcade.exit()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
