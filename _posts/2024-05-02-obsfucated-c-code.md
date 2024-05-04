---
layout: post
title: Obfuscating a Function &#8211; How not to write Code
modified:
categories: [Programming]
description: "A while back, I created a straightforward function to convert an integer into a new format, resulting in clear code. However, I inexplicably chose to obscure its purpose, leading to the following outcome: Read more in this post..."
tags: []
thumbnail: assets/img/computer-program-code_1385-530.jpg
giscus_comments: true
share:
date: 2024-05-02T15:01:50+02:00
---

Some time ago, I had to write a pretty simple function that converts an integer value into a new "format." The function ended up being easy-to-read code. For reasons I do not remember, I decided to obfuscate the purpose of the function slightly, and I ended up with the following:

{% highlight C %}

#include <stdio.h>

char* whatDoIdo(unsigned int x, char *t) {
    int i=7,j=0,v=5000,p,z[7]={0x49,0x56,0x58,0x4c,0x43,0x44,0x4d};
    while(!(t[j]='\0')&&x&&(v/=5/((i--+1)%2+1))+1) {
        while(x>=v&&(x-=v)+1&&(t[j++]=z[i])+1);
        while(i&&x>=(p=v-v*(i%2+1)/10)&&(x-=p)+1&&(t[j++]=z[i-2+(i%2)])+1
          &&(t[j++]=z[i])+1);
    }
    return t;
}

int main() {
    unsigned int x = 123;
    char t[200] = {0};
    printf("%d : %s", x, whatDoIdo(x,t));
    return 0;
}
{% endhighlight %}
<!--- %* -->

If you run the code for different values of `x` in the function `main(),` you will quickly discover the function's purpose, `whatDoIdo().` If you are more dedicated, you can decrypt the code and guess its functionality without running it once. Indeed, you should prevent writing code like this at work or university since your colleagues/classmates or others who have to read your code most likely won't appreciate this kind of programming style.

<!--more-->

If you do not have a compiler at hand, you can take a look at some sample outputs that should appear familiar.

{% details Click here to see some examples %}
  {% highlight plaintext %}
  1  : I
  5  : V
  50 : L
  {% endhighlight %}
{% enddetails %}
<br>

Any guess? If not, then take a look at some more outputs:


{% details Click here to see more examples %}
  {% highlight plaintext %}
  87   : LXXXVII
  123  : CXXIII
  1846 : MDCCCXLVI
  {% endhighlight %}
{% enddetails %}
<br>

There is even an [annual contest for obfuscated C code](https://www.ioccc.org/) on [https://www.ioccc.org/](https://www.ioccc.org/). IIf you are interested in submitting an entry for the next contest, the degree of obfuscation should be significantly higher than in this trivial example. The winning entries of the past years are really worth looking at.
