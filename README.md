# juggling
Various computer vision and machine learning Python scripts
Required: Python3 OpenCV4+

# How to draw tails on juggling balls (using color tracking).

1. Optimize the video for tracking. Use lots of light, a high frame rate*, and use balls that are distinct colors.
2. Determine the HSV values for the color the balls with hsv_picker.py.
3. Using one of the tracking scripts track the locations of the balls. If the source video is great the balls are destinct colors, the best tracking script is tracking_colorspaces.py. If the balls are destinct color and the source video is not geat, use tracking_hybrid_colorspaces_opticalflow.py. If tracking by color is not an option, try using tracking_optical_flow.py.
4. The data should be saved in a .csv file. If there are three balls (three tracking points), there will be three .csv files. Manually combine these .csv files.
5. Using tracking_object_writer.py display the tracked objects in the video. The length of the tail can be modified using the tail_length parameter.


* A high frame rate is really helpful for several reasons. First and foremost, as frame rate increases, distance between a moving object in successive frames descreases. Objects are difficult to track if they move more than around 5 pixles per frame. 720p120fps is necessary for 3 to 4 ball tracking. For 5 to 7 ball tracking 1080p240 is necessary. A higher frame rate also decreases motion blur.
