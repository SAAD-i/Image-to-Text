from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import base64

app = Flask(__name__)

def text_to_image(text, background_color='red', font_color='black', font_path=None, font_size=50, image_size=(1920, 1080)):
    font = ImageFont.truetype(font_path if font_path else "arial.ttf", font_size)
    image = Image.new('RGB', image_size, color=background_color)
    draw = ImageDraw.Draw(image)

    margin = 20
    max_width = image_size[0] - 2 * margin

    def wrap_text(text, font, max_width):
        lines = []
        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            words = paragraph.split()
            line = ''
            while words:
                while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                    line += (words.pop(0) + ' ')
                lines.append(line.strip())
                line = ''
            lines.append('')  # Add a blank line to separate paragraphs
        return lines

    wrapped_text = wrap_text(text, font, max_width)
    if wrapped_text[-1] == '':
        wrapped_text.pop()

    line_height = draw.textbbox((0, 0), 'A', font=font)[3]
    total_text_height = line_height * len(wrapped_text)

    text_y = (image_size[1] - total_text_height) // 2

    for line in wrapped_text:
        text_width = draw.textbbox((0, 0), line, font=font)[2]
        text_x = (image_size[0] - text_width) // 2
        draw.text((text_x, text_y), line, font=font, fill=font_color)
        text_y += line_height

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    img_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    return img_data

@app.route('/', methods=['GET', 'POST'])
def text_to_img():
    text = ''
    img_data = None  # Initialize img_data outside the if block
    background_color = 'red'
    font_color = 'black'
    if request.method == 'POST':
        text = request.form['user_text']
        background_color = request.form['background_color']
        font_color = request.form['font_color']
        img_data = text_to_image(text, background_color, font_color)
    return render_template('index.html', text=text, img_data=img_data, background_color=background_color, font_color=font_color)

@app.route('/download_image')
def download_image():
    text = request.args.get('text')
    background_color = request.args.get('background_color', 'red')
    font_color = request.args.get('font_color', 'black')
    if text:
        img_data = text_to_image(text, background_color, font_color)
        img_byte_arr = io.BytesIO(base64.b64decode(img_data.encode('utf-8')))
        img_byte_arr.seek(0)
        return send_file(img_byte_arr, mimetype='image/jpeg', as_attachment=True, download_name='output.jpg')
    else:
        return "Error: No text provided for download."

if __name__ == '__main__':
    app.run(debug=True)
