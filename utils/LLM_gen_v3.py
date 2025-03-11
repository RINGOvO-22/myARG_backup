import os
from volcenginesdkarkruntime import Ark
import json

'''
Final output file: fakeSV_for_ARG
'''

def rationale_gen(text):
    client = Ark(
        # 从环境变量中读取您的方舟API Key
        api_key='c2001f1c-cea7-43ed-9eed-928d2939f56e',
        # 深度推理模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
        timeout=1800,
        )
    messages=[
            {"role": "user", "content": "这是一个视频的misinformation detection任务(基于text)。\
            我需要你帮我分别从文本描述的角度和相关常识的的角度对主要内容各进行一段30字左右的真伪分析,\
            并在每个角度的分析后面分别给出‘real’或‘fake’的预测。根据以上问题，严格按照如下格式回答：\
            回答只包含一行, 分为四部分, 第一部分是文本描述, \
            第二部分是对它的预测。第三部分是相关常识，第四部分是常识角度的预测。相邻的部分由一个“====split====”分开\
            只回复回答内容本身，不要包含这四部分内容本身以外的任何额外内容。\
            视频的相关文本包含keywords, title, comments, author_intro, 以及一段视频ocr识别内容或者一段asr识别内容, 和summary。\
            拼接后的文本内容如下:"+text}
        ]
    response = client.chat.completions.create(
        # 替换 <Model> 为模型的Model ID
        model="deepseek-r1-250120",
        messages=messages,
        stream=True,
    )
    # 当触发深度推理时，打印思维链内容
    reasoning_content = ""
    content = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
            reasoning_content += chunk.choices[0].delta.reasoning_content
            # print(chunk.choices[0].delta.reasoning_content, end="")
        else:
            content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="")
    
    # 提取四部分回复的内容
    lines = content.strip().split('====split====')
    if len(lines) >= 4:
        result = {
            "td_rationale": lines[0],
            "td_pred": lines[1],
            "cs_rationale": lines[2],
            "cs_pred": lines[3],
        }
    else:
        result = {"error": "响应内容不足"}

    # 保存到JSON文件
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    return result
    
def build_text(item):
    text = ''
    text += 'keywords: ' + (item.get('keywords') or 'None') + '\n'
    text += 'title: ' + (item.get('title') or 'None') + '\n'
    comments = item.get('comments')
    text += 'comments: ' + ', '.join(comments) if comments else 'None' + '\n'
    text += 'author_intro: ' + (item.get('author_intro') or 'None') + '\n'

    # if needOCR false needASR true use asr, otherwise use ocr
    if item.get('needOCR') == False and item.get('needASR') == True:
        print('ASR used!\n')
        text += 'asr_result: ' + (item.get('asr') or 'None') + '\n'
    else:
        ocr_result = item.get('ocr', 'None').replace('\t', '').strip()
        text += 'ocrn_result: ' + ocr_result + '\n'

    text += 'summary: ' + (item.get('summary') or 'None') + '\n'
    return text

if __name__ == '__main__':
    # test_round = 2

    # 读取 JSON 文件/set output file path
    directory = './data/split_v3/'

    filename = 'data_complete.json' # input file name
    train_filename = 'small_train.txt'
    valid_filename = 'small_valid.txt'
    test_filename = 'small_test.txt'
    output_train_filename = 'train_v3.json'
    output_valid_filename = 'val_v3.json'
    output_test_filename = 'test_v3.json'

    file_path = os.path.join(directory, filename)
    # output_file_path = os.path.join(directory, output_filename)
    train_path = os.path.join(directory, train_filename)
    valid_path = os.path.join(directory, valid_filename)
    test_path = os.path.join(directory, test_filename)
    output_train_path = os.path.join(directory, output_train_filename)
    output_valid_path = os.path.join(directory, output_valid_filename)
    output_test_path = os.path.join(directory, output_test_filename)

    # get indices of train & valid & test samples
    train_idx_list = []
    val_idx_list = []
    test_idx_list = []
    
    # read from files
    with open(train_path, 'r', encoding='utf-8') as file:
        train_idx_list = file.readlines()
    train_idx_list = [line.strip() for line in train_idx_list]

    with open(valid_path, 'r', encoding='utf-8') as file:
        val_idx_list = file.readlines()
    val_idx_list = [line.strip() for line in val_idx_list]

    with open(test_path, 'r', encoding='utf-8') as file:
        test_idx_list = file.readlines()
    test_idx_list = [line.strip() for line in test_idx_list]

    # start reading complete dataset
    item_counter = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        # data = json.load(file)

        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line:  # 确保行不为空
                item = json.loads(line)
                item_counter += 1
                print('\n\n===========================================\n\nSample #%d:' % item_counter) 
            
            # print('\n===========================================\n\nlast %d round:' % test_round)
            
            # print('\nvideo_id:')
            # print(item.get('video_id'))
            video_id = item.get('video_id')

            # 初始化结果列表
            if video_id in train_idx_list:
                print("(Training sample)")
                output_path = output_train_path
            elif video_id in val_idx_list:
                print("(Validation sample)")
                output_path = output_valid_path
            elif video_id in test_idx_list:
                print("(Test sample)")
                output_path = output_test_path
            else:
                print("Not sampled !")
                continue

            # print('\npublish_time_norm :')
            # print(item.get('publish_time_norm'))
            time = item.get('publish_time_norm')

            # 处理 annotation
            annotation = item.get('annotation')
            # if annotation in ['假', '辟谣']:
            if annotation in '假':
                annotation = 'fake'
            elif annotation == '真':
                annotation = 'real'
            elif annotation == '辟谣':
                print('find 辟谣')
                continue
            else:
                # annotation = 'unknown'  # 如果 annotation 值不在预期范围内
                annotation = 'fake'
            # print('\nannotation:')
            # print(annotation)

            text=build_text(item)
            
            results = []
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as json_file:
                    results = json.load(json_file)

            # generate rationale & prediction using LLM
            # print(f'\ntext:\n{text}\n\n')
            LLM_result = rationale_gen(text)
            
            if 'fake' in LLM_result['td_pred']:
                LLM_result['td_pred'] = 'fake'
            if 'real' in LLM_result['td_pred']:
                LLM_result['td_pred'] = 'real'

            if 'fake' in LLM_result['cs_pred']:
                LLM_result['cs_pred'] = 'fake'
            if 'real' in LLM_result['cs_pred']:
                LLM_result['cs_pred'] = 'real'
            
            LLM_result['content'] = text
            LLM_result['label'] = annotation
            LLM_result['time'] = time
            LLM_result['source_id'] = video_id
            LLM_result['split'] = "train"
            if annotation == LLM_result['td_pred']:
                LLM_result['td_acc'] = 1
            else:
                LLM_result['td_acc'] = 0
            if annotation == LLM_result['cs_pred']:
                LLM_result['cs_acc'] = 1
            else:
                LLM_result['cs_acc'] = 0

            # 将结果添加到列表中
            results.append(LLM_result)
            # 每次循环后写入更新后的结果到文件
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(results, json_file, ensure_ascii=False, indent=4)

            # test_round -= 1
            # if test_round <= 0:
            #     break
