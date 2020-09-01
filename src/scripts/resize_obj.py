from PIL import Image
def do_resize(w, l):
    img = Image.open('obj.png')
    new_img = img.resize((int(w), int(l)))
    new_img.save("obj.png", "PNG", optimize=True)
