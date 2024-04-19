from trip_plan import create_trip_plan

import os
from trip import Trip
from openai import OpenAI


def init_env():
    # 设置环境变量或直接在LangChain配置中设置API密钥
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10887'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10887'
    os.environ['OPENAI_API_KEY'] = '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'

    client = OpenAI()
    return client


if __name__ == "__main__":
    output_pdf_path = 'Chongqing_Itinerary.pdf'

    client = init_env()
    trip = Trip("Chongqing", 2, 3)

    create_trip_plan(trip, output_pdf_path, client)
