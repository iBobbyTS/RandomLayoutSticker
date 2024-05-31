import os
import random
from PIL import Image
import numpy as np

# Arguments
inp_path = 'input_march7th'  # abs/rel path to the folder with images
out_name = 'output_march7th'  # abs/rel path to the output image without extension, image will be saved as output.png and output.tif
bg_color = (147, 220, 255)  # march7th
padding = 1.3  # padding factor
lines = 10  # number of lines
cols = 16  # number of columns


files = os.listdir(inp_path)
files.sort()
if '.DS_Store' in files: files.remove('.DS_Store')

images_pil = [Image.open(f'{inp_path}/{i}') for i in files]
max_width = max([i.size[0] for i in images_pil])
max_height = max([i.size[1] for i in images_pil])
# pad the images with white background to make them all the same size, image goes to center
for i in range(len(images_pil)):
    new_image = Image.new('RGBA', (max_width, max_height), (255, 255, 255, 0))
    new_image.paste(images_pil[i], ((max_width - images_pil[i].size[0]) // 2, (max_height - images_pil[i].size[1]) // 2))
    images_pil[i] = new_image
print(f'Padded images to {images_pil[0].size}')
# expand the image with white background and keep original part in the middle
for i in range(len(images_pil)):
    # create a new image with white background
    new_image = Image.new('RGBA', (int(images_pil[i].size[0] * padding), int(images_pil[i].size[1] * padding)), (255, 255, 255, 0))
    # paste the original image in the middle
    new_image.paste(images_pil[i], (int(images_pil[i].size[0] * (padding - 1) / 2), int(images_pil[i].size[1] * (padding - 1) / 2)))
    images_pil[i] = new_image
expanded_width, expanded_height = images_pil[0].size
print(f'Expanded images to {images_pil[0].size}')
images_np = [np.array(i).astype(np.float64) for i in images_pil]
output_np = np.zeros((int(images_pil[0].size[1] * lines), int(images_pil[0].size[0] * (cols+1)), 4), dtype=np.float64)
print(f'Output size: {output_np.shape}')
for i in range(lines):
    for j in range(cols+1-i%2):
        offset_x = expanded_width * j + (expanded_width//2*(i%2))
        offset_y = expanded_height * i
        print(f'Line: {i}, Col: {j}, Image s ize: {expanded_width}x{expanded_height}, Destination: y={offset_y}:{offset_y+expanded_height}, x={offset_x}:{offset_x+expanded_width}. y*x:', output_np[offset_y:offset_y+expanded_height, offset_x:offset_x+expanded_width].shape, output_np.shape)
        output_np[offset_y:offset_y+expanded_height, offset_x:offset_x+expanded_width] = random.choice(images_np)

output_np[output_np[:, :, 3] == 0] = [*bg_color, 255]
output_np = output_np[:, expanded_width//2:-expanded_width//2]
output_np = output_np.round().clip(0, 255).astype(np.uint8)
output_pil = Image.fromarray(output_np)
output_pil.convert("RGB").save(out_name+'.tif')
os.system(f'convert {out_name}.tif -alpha off -quality 90 -depth 8 {out_name}.png')
