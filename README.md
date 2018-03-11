## pymgur

### A pastebin for images

pymgur is a tool that allow posting images on a local instance
and serve them afterwards (analog to [pastebin](https://github.com/lordelph/pastebin))

It's designed so that anyone can run his own instance relatively easily,
and to allow you to easily post images via curl


Requirements are :

- python 3
- flask (web framework)
- pillow (image library)

Images are stored locally on the filesystem and image metadata is stored in a sqlite database


A demo site is available at http://pymgur.chivil.com/


Current version should he usable but totally lacks configuration (hard-coded in the init file)

README to be continued …