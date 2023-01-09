# A-Classic-Brick-Game
A reproduction of the classic arcade game Breakout first published by Atari, Inc. in 1976. The original game was first designed by Steve Wozniak.


Two versions in this repository:

 1. Classic game physics i.e. depending where the ball bounces on the paddle the ball will be returned at a relative angle from -60 to +60 deg, with 0 deg (vertical) at the center.
 When hitting a brick corner the ball is returned at 45 deg.
 
 2. Real world bounce angles i.e. the shape of the surface of the pad simulates a curved surface as a function of a sin wave from -60 to +60 deg, with 0 deg (horizontal surface) at the center. When hitting the paddle the ball is returned at a calculated reflection angle.
 When hitting a brick corner the corner is treated as a 45 deg surface and the ball is retuned based on the calculated reflection angle.
 
 Version 2 is just for fun, in reality it is unpractical as it's possible to rebound the ball at a very shallow angle. The y-vector of the ball is kept constant to compensate for the time it takes the ball, travelling at a shallow angle, to reach the top and get back down. This also means that the ball's velocity increases as it's angle gets shallower.
 
 It is also possible to bounce the ball off the paddle in such a way that the ball keeps travelling down off the screen. This happens when the ball travelling at a shallow angle hits the farther side of the paddle, where the angle of the paddle is closer to parallel with the ball angle.
 
 A pdf slide deck is included in the repo showing the calculation of the reflective bounce of the ball against the paddle.
 
