# LLM API

deepseek：

* [文档](https://api-docs.deepseek.com/zh-cn/)
* 指定模型:
  * DeepSeek-V3: model='deepseek-chat' 
  * DeepSeek-R1: model='deepseek-reasoner'



## DeepSeek 官方

1. 官网创建 API Key

2. python 调用 api (使用 openAI sdk):

   * **单轮对话**:

     ```python
     # Please install OpenAI SDK first: `pip3 install openai`
     
     from openai import OpenAI
     
     client = OpenAI(api_key="<your key>", base_url="https://api.deepseek.com")
     
     response = client.chat.completions.create(
         model="deepseek-chat",
         messages=[
             {"role": "system", "content": "You are a helpful assistant"},
             {"role": "user", "content": "你是谁"},
         ],
         stream=False
     )
     
     print(response.choices[0].message.content)
     ```

     * 代码中，{"role": "user", "content": "你是谁"}中的 content 是单轮对话中你的问题。
       代码执行后返回：
       您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-V3。如您有任何任何问题，我会尽我所能为您提供帮助。

   * **多轮对话**：

     下面会连续问两个问题，第一个问题是世界上最高的山是什么？第二个问题是那第二高的山呢？大模型会记住你一个问题来回答第二个问题，代码中也可以看到第二轮对话是添加了第一个消息的内容。

     ```python
     from openai import OpenAI
     client = OpenAI(api_key="<your key>", base_url="https://api.deepseek.com")
     
     # Round 1
     messages = [{"role": "user", "content": "世界上最高的山是什么?"}]
     response = client.chat.completions.create(
         model="deepseek-chat",
         messages=messages
     )
     
     messages.append(response.choices[0].message)
     print(f"Messages Round 1: {messages}")
     
     # Round 2
     messages.append({"role": "user", "content": "那第二高的山呢?"})
     response = client.chat.completions.create(
         model="deepseek-chat",
         messages=messages
     )
     
     messages.append(response.choices[0].message)
     print(f"Messages Round 2: {messages}")
     ```

     * 第二轮对话是基于第一个基础之上的。在**第一轮**请求时，传递给 API 的 `messages` 为：[     {"role": "user", "content": "界上最高的山是什么?"} ]
     * 在**第二轮**请求时：
       1. 要将第一轮中模型的输出添加到 `messages` 末尾
       2. 将新的提问添加到 `messages` 末尾



## 第三方平台

### 火山引擎

* [python SDK](https://www.volcengine.com/docs/82379/1319847)
* [调用 DeepSeek R1](https://www.volcengine.com/docs/82379/1449737)



第一步：

1. 获取 API Key，后续用于调用模型推理服务的鉴权。
2. 在开通管理页开通所需模型的服务。
3. 在模型列表获取所需模型的ID（Model ID），后续调用模型服务时需使用。



快速开始：

即单论对话

* 其中注意使用下面命令将API Key配置为环境变量ARK_API_KEY。

  ```
  export ARK_API_KEY="<ARK_API_KEY>"
  ```

  * 我在 windows 环境，所以手动去环境变量里添加了。

  

# 记录

* LLM 处理 json 时，在开头和结尾加了个 `[]`
* 

# 问题

* 联网功能？
* 价格？
* llm 预测的 real 好像挺少的。