
To obtain enough images for the deep learning project, use these snippt in the JavaScript console(open with `View`->`Developer`->`JavaScript Console`) of chrome browser:

```js
// pull down jquery into the JavaScript console
var script = document.createElement('script');
script.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(script);

// grab the URLs
var urls = $('.rg_di .rg_meta').map(function() { return JSON.parse($(this).text()).ou; });

// write the URls to file (one per line)
var textToSave = urls.toArray().join('\n');
var hiddenElement = document.createElement('a');
hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
hiddenElement.target = '_blank';
hiddenElement.download = 'urls.txt';
hiddenElement.click();
```

* Should use them **twice**, **`past` -> `Enter`** then **`past` -> `Enter`** again, feel free to edit the download file name before clicking the second `Enter`.
* The downloaded file contains all urls line by line of images you saw in the Google image search page.
* In case of you misleaded by my poor English expression, watch the author's video:  
    https://www.youtube.com/watch?v=JrVZ0QM_z-o

To download them please use the `download_images.py`, execute `python download_images.py -h` or read the source code to check the usage.


