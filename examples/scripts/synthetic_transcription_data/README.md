# Toy OCR data

This is a toy dataset used to illustrate how Stringalign can detect common transcription errors and visualize them.
The data is based on an excerpt from a digitized copy of [*Lærebog i de forskjellige Grene af Huusholdningen* by Hanna Winsnes (1846)](https://www.nb.no/items/URN:NBN:no-nb_digibok_2009111210001) from the digitized collection of the National Library of Norway.

In particular, the dataset consists of:

* `image.png`
  * Snippet from [https://www.nb.no/items/URN:NBN:no-nb_digibok_2009111210001?page=37](https://www.nb.no/items/URN:NBN:no-nb_digibok_2009111210001?page=37) used to transcribe the text
* `line{i:02d}.jpg`
  * An image containing the `i`-th text-line from `image.png`
* `reference.txt`
  * Manually transcribed text based on `image.png`
* `predicted.txt`
  * The "predicted" text, made by switching out letters in the reference with letters that are visualy similar in the source image.
