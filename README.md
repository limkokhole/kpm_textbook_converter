# kpm_textbook_converter
This python code convert ePUB code to html version which can handle more pages and offline readable.

Ensures your system has youtube-dl and python installed. Download ebooks from kpm textbook app, then adb pull /sdcard/Android/data/com.kotabuku.kpm/files/long_digits , then simply run `python textbook_converter.py` on the desired folder or parent folder. After done, you can right-click content.html to open with your desired web browser (recommend Firefox/Chrome since Edge has problem to shows some pages. While Firefox preferred to use than Chrome because Chrome seems stuck if got many frames+videos running.)

This offline version included videos and games, except google map stuff.

