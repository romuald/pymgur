import io
import PIL.Image

def image_has_transparency(image):
    """
    Determine if an image has transparency, by checking
    its mode/metadata, or pixel values for RBGA

    """
    # easy enough
    if image.mode in ('RGB', 'L', '1', 'CMYK', 'YCbCr', 'I', 'F'):
        return False

    # seems to work with GIF/PNG
    if image.mode == 'P':
        return 'transparency' in image.info

    # a bit tricky, they mostly have transparent pixels
    # (due to optimizers saving images as RGB), but they may
    # as well have their entire alpha channel opaque
    if image.mode == "RGBA":
        _, _, _, (alphamin, _) = image.getextrema()
        return alphamin < 255

    return True

def create_preview(filename, image, size):
    """Creates a smaller static image, used for thumbnail and previews"""
    # Thumbnail starts here
    ext = "png" if image_has_transparency(image) else "jpg"
    filename += '.%s' % ext

    # thumbfilename = '%s%s.%s' % (prefix, uid, ext)
    # thumbpath = fspath_for_name(thumbfilename)

    image = image.copy()
    image.thumbnail((size, size), PIL.Image.ANTIALIAS)
    with io.open(filename, 'wb+') as output:
        if ext == "jpg":
            # In case of indexed palette, JPEG mut be converted to RGB
            image = image.convert('RGB')
            image.save(output, quality=75, optimize=True, progressive=True)
        else:  # png
            image.save(output, optimize=True)

    # thumbnail.close()
    image.close()
    return filename
    return output, ext

def request_wants_json(request):
    # http://flask.pocoo.org/snippets/45/
    best = request.accept_mimetypes.best_match(('application/json',
                                                'text/html'))
    return (
            best == 'application/json'
            and request.accept_mimetypes[best] >
                request.accept_mimetypes['text/html']
            )