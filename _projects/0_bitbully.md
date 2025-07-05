---
layout: page
title: BitBully
description: One of the fastest and perfect-playing Connect-4 solvers around
img: assets/img/project_bitbully/bitbully-logo-full.png
# redirect: https://unsplash.com
importance: 1
category: fun
related_publications: true
giscus_comments: true
---


{% cite Thill12 %}

{% cite Thill2015a %}

{% cite bagh16b %}

{% cite Thil14 %}

{% cite Thil12 %}


<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-1.png" title="Connect4 (1)" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-2.png" title="Connect4 (2)" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-3.png" title="Connect4 (3)" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    <b>From Opening to Victory: From Opening Moves to Victory.</b> The image shows three key stages of a Connect 4 match — an early board with initial placements, a mid-game filled with tension and strategy, and the final state where yellow wins by connecting four discs. Connect 4 is a two-player game where discs are dropped into columns, aiming to form a straight line of four. It blends tactical planning with defensive play, and despite its simplicity, it’s a classic example of solvable strategy games in AI.
</div>
<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/5.jpg" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    This image can also have a caption. It's like magic.
</div>

You can also put regular text between your rows of images, even citations {% cite einstein1950meaning %}.
Say you wanted to write a bit about your project before you posted the rest of the images.
You describe how you toiled, sweated, _bled_ for your project, and then... you reveal its glory in the next row of images.

<div class="row justify-content-sm-center">
    <div class="col-sm-8 mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/6.jpg" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm-4 mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/11.jpg" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    You can also have artistically styled 2/3 + 1/3 images, like these.
</div>

The code is simple.
Just wrap your images with `<div class="col-sm">` and place them inside `<div class="row">` (read more about the <a href="https://getbootstrap.com/docs/4.4/layout/grid/">Bootstrap Grid</a> system).
To make images responsive, add `img-fluid` class to each; for rounded corners and shadows use `rounded` and `z-depth-1` classes.
Here's the code for the last row of images above:

{% raw %}

```html
<div class="row justify-content-sm-center">
  <div class="col-sm-8 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/6.jpg" title="example image" class="img-fluid rounded z-depth-1" %}
  </div>
  <div class="col-sm-4 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/11.jpg" title="example image" class="img-fluid rounded z-depth-1" %}
  </div>
</div>
```

{% endraw %}
