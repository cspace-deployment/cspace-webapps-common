import sys

# https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil

image1 = '8fe92c97.jpg'
image2 = 'botgarden_watermark_520x520_trans_white.png'
 
from PIL import Image

if 'paste' in sys.argv:
    background = Image.open(image1)
    foreground = Image.open(image2)
    
    # foreground.convert('RGBA')
    
    background.paste(foreground, (0, 0), foreground)
    #background.show()
    
    background.save(filename='watermark.jpg')
    print 'save paste %s' % 'watermark.jpg'
  
    sys.exit(0)

# https://stackoverflow.com/questions/32034160/creating-a-watermark-in-python
from wand.image import Image

with Image(filename=image1) as background:
    with Image(filename=image2) as watermark:
        background.watermark(image=watermark, transparency=0.60)
    background.save(filename='watermark.jpg')
    print 'save wand %s' % 'watermark.jpg'

