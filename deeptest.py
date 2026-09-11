from openai import OpenAI
import time 
import uvicorn
# 从 openai 库中导入流式返回的数据类型
from openai.types.chat import ChatCompletionChunk
#from openai.types.chat import ChatCompletion
from fastapi import FastAPI
from pydantic import BaseModel
import os
#from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse,StreamingResponse

#创建服务器
#存每个会话的对话历史
sessions = {}
app=FastAPI()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("错误：找不到 DEEPSEEK_API_KEY，请先在系统环境变量里设置它！")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
class Q(BaseModel):
   q:str
   se_id:str=""

@app.get("/")
async def hello():
   return FileResponse("dh.html")


messages=[
   {"role": "system",
    "content": "你是金发美少女，红瞳孔，参考二阶堂真红人设。"
   },
]

@app.post("/ask")
async def ask(req: Q):        # ① 接收前端数据
    def generate():  
        fu=""
        messages.append({"role": "user", "content": req.q})                  # ② 定义生成器
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            stream=True,               # ③ 开启流式
        )
        for chunk in response:         # ④ 逐块遍历
            if chunk.choices and chunk.choices[0].delta.content:
                c=chunk.choices[0].delta.content  # ⑤ 逐字返回
                fu+=c
                yield c
                time.sleep(0.03)
        messages.append({"role": "assistant", "content": fu})        
    return StreamingResponse(generate(), media_type="text/plain")  # ⑥ 流式响应
        

if __name__ == "__main__":
   port = int(os.getenv("PORT", 7000))
   uvicorn.run("deeptest:app", host="0.0.0.0", port=port)
    



    
