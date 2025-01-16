from PIL import Image, ImageDraw
import math

def create_minimal_filter_icon():
    # 创建一个128x128的透明背景图像
    size = 128
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 设置颜色
    primary_color = (127, 127, 213, 255)  # #7F7FD5
    secondary_color = (107, 107, 213, 255)  # 深一点的紫色
    
    # 绘制重叠的文档效果
    doc_width = size * 0.5
    doc_height = size * 0.6
    margin = size * 0.2
    
    # 绘制三个错开的文档轮廓
    offsets = [(0, 0), (-10, -10), (-20, -20)]
    for offset_x, offset_y in offsets:
        x = margin - offset_x
        y = margin - offset_y
        
        # 文档的路径点
        doc_points = [
            (x, y),  # 左上
            (x + doc_width, y),  # 右上
            (x + doc_width, y + doc_height),  # 右下
            (x, y + doc_height),  # 左下
        ]
        draw.polygon(doc_points, outline=primary_color, width=2)
        
        # 添加文档内的横线
        line_margin = doc_height * 0.2
        line_space = (doc_height - 2 * line_margin) / 3
        for i in range(3):
            line_y = y + line_margin + i * line_space
            draw.line(
                [(x + doc_width*0.2, line_y), 
                 (x + doc_width*0.8, line_y)],
                fill=primary_color, width=1
            )
    
    # 绘制一个圆形选择标记
    circle_size = size * 0.25
    circle_x = size - margin - circle_size/2
    circle_y = size - margin - circle_size/2
    
    # 绘制圆圈
    draw.ellipse(
        [(circle_x - circle_size/2, circle_y - circle_size/2),
         (circle_x + circle_size/2, circle_y + circle_size/2)],
        outline=secondary_color, width=3
    )
    
    # 绘制勾号
    check_size = circle_size * 0.4
    check_points = [
        (circle_x - check_size*0.5, circle_y),
        (circle_x - check_size*0.1, circle_y + check_size*0.4),
        (circle_x + check_size*0.5, circle_y - check_size*0.4)
    ]
    draw.line(check_points, fill=secondary_color, width=3)

    # 保存为不同尺寸的ICO文件
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
    image.save('filter.ico', sizes=icon_sizes)

if __name__ == "__main__":
    create_minimal_filter_icon() 