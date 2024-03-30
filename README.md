# pyRaycasterEngine
![image](https://github.com/Turtlemaster13/pyRaycasterEngine/assets/104543638/b410f56f-3f42-48c1-b7f3-6c06ba3a55fe)

I put it on github now yay!


I read this and implemented my own version in python:
https://lodev.org/cgtutor/raycasting.html 

In my code there was some cliping in the corner of walls, where single rays would sneak through and hit the other side.  To fix this insted of figuring out what the problem was I just took the standerd deviation of the rays near it, and if the ray was 2 standerd errors away I took an average of all the rays in that grouping and replace the outlier with it. It is pretty silly but it was a fun chalange.
