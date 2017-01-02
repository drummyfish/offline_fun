# offline_fun
These are scripts I wrote to download my favorite webpages for offline browsing, to have my own mini-internet for those difficult times I'm on a bus and there's no WIFI.

You can use it too, but remember, I made this for myself and if it's not good enough for you, please don't try to kill me. Rather fork and fix and maybe make a PR :)

How does it work?

1. Write pages and other files you want downloaded to the content_file.txt. The file format is this (you can take a look to my content file):
  - URLs of files to be downloaded are on separate pages.
  - Each URL can be followed by optional modifiers, separated by tabs. Supported modifiers are now:
    - proc:f1,f2,... - Processing functions to apply to the downloaded file. There are a few functions, such as wiki (for wikipedia) or small (for making an image small), implemented in proc_functions.py you can use here.
    - css:filename.css - CSS which the page should use. You can use my general g.css file here, or provide your own (place in the folder with the script).
    - under:name - Cathegory under which the page will be listed in the index file.
    - forcetype:extension - Force filetype, not used often.
  - Empty lines or lines starting with # are ignored.
2. Run make_the_fun.py with Python 2.7 and wait for it to download the files. If there are errors, you can retry, networks are unpredictable.
3. You now have your mini internet in the output folder - copy it to your device.
4. Profit.

Optionaly you can add your own file processing functions to proc_functions.py.
