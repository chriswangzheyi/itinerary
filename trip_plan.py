from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def get_places_and_activities(client, prompt_text):
    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt_text,
            max_tokens=1000,
            temperature=0.6
        )
        print("response: ", response)
        return response.choices[0].text.strip() if response.choices else None
    except Exception as e:
        print(f"Error during API call: {e}")
        return None


def custom_prompt(trip):
    # 定义详细的描述字符串
    json_description = f'''{{
        "day1": {{
            "1": {{
                "time": "9:00", 
                "place": "白金汉宫", 
                "activity": "参观英国君主的官邸。上午11点观看卫兵换岗仪式。"
            }},
            "2": {{
                "time": "12:00", 
                "place": "威斯敏斯特教堂", 
                "activity": "参观令人惊叹的哥特式教堂，许多皇室婚礼和加冕仪式都在这里举行。"
            }},
            "3": {{
                "time": "14:00", 
                "place": "附近的酒吧", 
                "activity": "享受一顿传统的英式午餐"
            }}，
            "4": {{
                "time": "19:00", 
                "place": "伦敦安大略希尔顿逸林酒店", 
                "activity": "入住酒店"
            }}
        }},
        "day2": {{
            "1": {{
                "time": "9:00", 
                "place": "大英博物馆", 
                "activity": "参观世界上最大和最全面的博物馆之一，拥有超过800万件文物"
            }},
            "2": {{
                "time": "12:00", 
                "place": "考文特花园", 
                "activity": "享用午餐，参观熙熙攘攘的市场和购物区，享用午餐和购买纪念品。"
            }},
            "3": {{
                "time": "14:00", 
                "place": "伦敦眼", 
                "activity": "参观巨大的摩天轮，欣赏城市的美景。"
            }}，
            "4": {{
                "time": "19:00", 
                "place": "伦敦安大略希尔顿逸林酒店", 
                "activity": "入住酒店"
            }}
        }}
    }}'''

    prompt_text = f'''
    Create a comprehensive  {trip.get_num_days()}-day itinerary for visiting {trip.get_city()}. we have {trip.get_num_travelers()} 
    people. Include popular tourist attractions, food experiences, and cultural activities, 3 items per day max. use the same language as {trip.get_city()}. 


    Format:
    {json_description}
    '''
    return prompt_text


def parse_activities(response_text):
    # 假设响应文本是完整的JSON-like字符串，我们首先将其分割成每天的部分
    import json

    try:
        # 尝试将响应字符串转换为字典
        data = json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to decode JSON. Checking if response is a JSON-like structure from an example.")

        # 因为实际输出示例不是有效的JSON，我们需要手动解析
        data = {}
        days_data = response_text.split('},\n    "day')
        for day in days_data:
            day_index = day[0]
            events = {}
            activities = day.split(',\n        "')
            for activity in activities[1:]:  # 跳过第一个元素，它是"dayX": { 的一部分
                if activity.strip():
                    time, details = activity.split(': {\n            "time": "')
                    details_parts = details.split(', \n            "place": "')
                    time = details_parts[0].strip('"')
                    place, activity_desc = details_parts[1].split(', \n            "activity": "')
                    place = place.strip('"')
                    activity_desc = activity_desc.strip('"\n        }').rstrip(',').rstrip('"}')
                    events[time] = {"time": time, "place": place, "activity": activity_desc}
            data[f'day{day_index}'] = events

    activities_list = []
    # 将字典转换为列表的列表格式
    for day_key, day_value in data.items():
        day_activities = []
        for event in day_value.values():
            day_activities.append([event['time'], event['place'], event['activity']])
        activities_list.append(day_activities)

    return activities_list


def create_trip_plan(trip, output_filename, client):
    # 在生成 PDF 前加载中文字体
    pdfmetrics.registerFont(TTFont('SimSun', 'font/simsun.ttf'))  # 这里假设宋体字体文件名为simsun.ttf

    prompt_text = custom_prompt(trip)
    activities_text = get_places_and_activities(client, prompt_text)
    days_activities = parse_activities(activities_text)  # 解析活动数据

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        name='Custom',
        parent=styles['BodyText'],
        fontName='SimSun',  # 使用宋体字体
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,  # 文本对齐方式
        spaceAfter=0,
        wordWrap='LTR'  # 从左到右的文本方向
    )

    title_style = styles['Title']
    title_style.fontName = 'SimSun'  # 使用宋体字体
    title = Paragraph(f'{trip.get_city()} 旅行计划', title_style)

    elements = [title, Spacer(1, 0.2 * inch)]

    if not days_activities:
        error_message = "No valid activities data to create PDF."
        print(error_message)
        elements.append(Paragraph(error_message, custom_style))
    else:
        for day_num, day_activities in enumerate(days_activities, start=1):
            if not day_activities:
                error_message = f"No activities found for Day {day_num}."
                elements.append(Paragraph(error_message, custom_style))
            else:
                day_title = Paragraph(f'Day {day_num}', styles['Heading2'])
                elements.append(day_title)

                table_data = [['Time', 'Place', 'Activity']] + [
                    [Paragraph(cell, custom_style) for cell in row] for row in day_activities
                ]

                table = Table(table_data, colWidths=[2.05 * inch, 2.05 * inch, 2.05 * inch])
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(table_style)

                elements.append(table)
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    print(f"PDF created successfully: {output_filename}")
