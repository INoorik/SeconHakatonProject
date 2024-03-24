from PIL import Image

img = Image.open("answer_level2.bmp")
source = Image.open("source_level2.jpg")
result = Image.new("RGB", (1920, 1080))

for i in range(1920):
    for j in range(1080):
        i_pix = img.getpixel((i, j))
        s_pix = source.getpixel((i, j))
        if i_pix:
            pass
        s_pix = ((s_pix[0] & 254) | (i_pix >> 7), s_pix[1], s_pix[2])
        result.putpixel((i, j), s_pix)


source.close()
img.close()
result.save("result.png")