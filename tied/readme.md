# TIED
**Text based Image EDitor**

uses python to load and manipulate images like traditional image editors, running the main "gui"`` should give you a live preview of the resulting image. 

.ed files for "edit", basically python but "live"

---

## functions

 - `edit(input image path)`
 loads an image from `input image path` (if valid) to edit 
 - `save(output image path)`
 saves the edited image to `output image path`
 - `print(text)`
 prints `text` to console
 - `for x in range(n):` 
 loops for n times, with x as counter. 
 - `hsv(h, s, v, a = 1)`
 converts an hsv color into an rgb color
 - `hex(hexadecimal string)`
 converts a hex color into an rgb color

### editing functions
`thickness`: positive number for thickness, -1 for fill  
`color`: the color of the object, in `(R, G, B)` format (0 - 255) 
 - `rectangle/rect(x1, y1, x2, y2, color, thickness)`  
 draws a rectangle from `(x1, y1)` to `(x2, y2)`  
 - `line(x1, y1, x2, y2, color, thickness)`  
 draws a line fron `(x1, y1)` to `(x2, y2)`  
 - `polygon(points, color, thickness, closed = True)`  
 draws a polygon on points `points`, can can be open if desired  
 - `path(points, color, thickness)`  
 draws a path on points `points`  
 - `text(x, y, content, color, thickness, size, font = 0)`  
 writes `content` at `(x, y)`, with choice for fonts[^1]  
    - `0` : `FONT_HERSHEY_SIMPLEX `       - normal size sans-serif font
    - `1` : `FONT_HERSHEY_PLAIN`          - small size sans-serif font
    - `2` : `FONT_HERSHEY_DUPLEX`         - normal size sans-serif font (more complex than FONT_HERSHEY_SIMPLEX)
    - `3` : `FONT_HERSHEY_COMPLEX`        - normal size serif font
    - `4` : `FONT_HERSHEY_TRIPLEX`        - normal size serif font (more complex than FONT_HERSHEY_COMPLEX)
    - `5` : `FONT_HERSHEY_COMPLEX_SMALL`  - smaller version of FONT_HERSHEY_COMPLEX
    - `6` : `FONT_HERSHEY_SCRIPT_SIMPLEX` - hand-writing style font
    - `7` : `FONT_HERSHEY_SCRIPT_COMPLEX` - more complex variant of FONT_HERSHEY_SCRIPT_SIMPLEX
    - `16` : `FONT_ITALIC`                - flag for italic font (usage: add `& 16` after normal font)
 - `ellipse(x1, y1, x2, y2, color, thickness, rotation = 0, startAngle = 0, endAngle = 360)`  
 draws an ellipse from `(x1, y1)` to `(x2, y2)` with rotation `rotation`, clipped to make an elliptical arc by specifying `startAngle` and `endAngle`  
 - `circle(x, y, radius, color, thickness)`  
 draws a circle at `(x, y)` with radius `radius`  
 - `arc(x, y, radius, startAngle, endAngle, color, thickness)`  
 draws an arc at `(x, y)` from `startAngle` to `endAngle`  
 - `bezier(x1, y1, x2, y2, x3, y3, x4, y4, color, thickness, samples = 20)`  
 draws a bezier curve defined by points `(x1, y1)`, `(x2, y2)`, `(x3, y3)`, `(x4, y4)` with the quality controlled by `samples`  
 - `convolute(kernel)`
 applies a custom kernel to the image through image convolution. Works with square kernels of odd widths and heights (3x3, 5x5, ...)
 - `color_balance(lift, gamma, gain)`
 applies color balancing based on the ASC-CDL algorithm. 
 - `hue(value)`
 shifts the hue by `value` degrees
 - `saturation(value)`
 multiplies the saturation by `value`
 - `contrast(value)`
 currently doesn't quite work, adjusts the contrast of the image
 - `brightness(value)`
 multiplies the brightness by `value`

### variables
 - getting `dim()`
 returns the dimensions of the image as `[x, y]`, access each dimension separately by following dim with `[0]` for x and `[1]` for y
 - getting `time` 
 returns the total seconds since the program started
 - setting `live` 
 sets whether or not the program should keep updating after drawing
 watch out for saving in live, this can create lots of files very fast
 TODO: print doesn't seem to quite work when live

 [^1]: credit for the font descriptions goes to www.codeyarns.com/tech/2015-03-11-fonts-in-opencv.html
