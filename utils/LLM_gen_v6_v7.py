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
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        timeout=1800,
        )
    messages=[
            {"role": "user", "content": f"这是一个视频的misinformation detection任务(基于text)。\
            帮我分别从文本描述的角度和相关常识的的角度,对主要内容各进行一段30字左右的真伪分析,\
            并在每个角度的分析后面分别给出‘real’或‘fake’的预测。根据以上问题，严格按照如下格式回答：\
            回答只包含一行, 分为四部分, 第一部分是文本描述, \
            第二部分是对它的预测。第三部分是相关常识，第四部分是常识角度的预测。相邻的部分由一个“====split====”分开\
            只回复内容本身，不要包含这四部分内容本身以外的任何额外内容。\
            视频的相关文本包含keywords, title, comments, author_intro, ocr识别内容, 一段asr识别内容, 和summary。\
            拼接后的文本内容如下: {text}. 例子：\
            输入：\"keywords: 老人带着孙子去超市赊米下跪\ntitle: 平凡的人，不平凡的爱！为你们点赞！\ncomments: 为老板点赞, 好人一生平安！, 想资助一下老婆婆，谁能找一下呀, 善有善报, 好人一生平安！, 看完流泪了！真正的需要帮助，希望每个好心人，都献点爱心，我碰到也会帮助, 好心人, 感动, 哎……心疼……, 好可怜, 好人有好报, 好心人点赞, 小孩长大会报恩的, 好人一生平安author_intro: 辛集发布带你看世界           \n视频投稿：VX：15511836658；邮箱：xinjifabu@163.com\nasr_result: 中文字幕提供本期视频就分享到这里\nocrn_result: 什么,我这里不除账的 孩子这一跪让人泪目! 我们昨天晚上就没有吃饭 已经十多天没有出门了 孩子这一跪让人泪目! 我奶奶是捡废品的 现在国家有个病毒 孩子这一跪让人泪目! 你看我,我拿给你们 孩子这一跪让人泪目!\n\"\
            输出：\"老人带着孙子去超市赊米下跪，视频展示感人的场景。====split====real====split====现实中超市通常不允许赊账，且 此类事件常见于网络虚假故事。====split====fake\""}
        ]
    response = client.chat.completions.create(
        model="deepseek-v3-241226",
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

    # # 保存到JSON文件
    # with open('output.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(result, json_file, ensure_ascii=False, indent=4)

    return result
    
def build_text_ocr_orAsr_andSum(item):
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

    with open('./data/split_v6/merged_data_2.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for sample in data:
            if sample['video_id'] == item.get('video_id'):
                text += 'summary: ' + (sample.get('summary_zh') or 'None') + '\n'
                break
    return text

def build_text_ocr_andAsr_andSum(item):
    text = ''
    text += 'keywords: ' + (item.get('keywords') or 'None') + '\n'
    text += 'title: ' + (item.get('title') or 'None') + '\n'
    comments = item.get('comments')
    text += 'comments: ' + ', '.join(comments) if comments else 'None' + '\n'
    text += 'author_intro: ' + (item.get('author_intro') or 'None') + '\n'

    text += 'asr_result: ' + (item.get('asr') or 'None') + '\n'
    ocr_result = item.get('ocr', 'None').replace('\t', '').strip()
    text += 'ocrn_result: ' + ocr_result + '\n'

    with open('./data/split_v7/merged_data_2.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for sample in data:
            if sample['video_id'] == item.get('video_id'):
                text += 'summary: ' + (sample.get('summary_zh') or 'None') + '\n'
                break
    return text

def build_text_ocr_andAsr(item):
    text = ''
    text += 'keywords: ' + (item.get('keywords') or 'None') + '\n'
    text += 'title: ' + (item.get('title') or 'None') + '\n'
    comments = item.get('comments')
    text += 'comments: ' + ', '.join(comments) if comments else 'None' + '\n'
    text += 'author_intro: ' + (item.get('author_intro') or 'None') + '\n'

    text += 'asr_result: ' + (item.get('asr') or 'None') + '\n'
    ocr_result = item.get('ocr', 'None').replace('\t', '').strip()
    text += 'ocrn_result: ' + ocr_result + '\n'

    # text += 'summary: ' + (item.get('summary') or 'None') + '\n'
    return text

# ocr and asr
def run_v6():
    # test_round = 2

    # 读取 JSON 文件/set output file path
    directory = './data/split_v6/'

    filename = 'data_complete_v5.json' # input file name
    train_filename = 'small_train.txt'
    valid_filename = 'small_valid.txt'
    test_filename = 'small_test.txt'
    output_train_filename = 'train_v6.json'
    output_valid_filename = 'val_v6.json'
    output_test_filename = 'test_v6.json'

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

            text=build_text_ocr_andAsr(item)
            
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

# ocr and asr and summary
def run_v7():
    # test_round = 2

    # 读取 JSON 文件/set output file path
    directory = './data/split_v7/'

    filename = 'data_complete_v5.json' # input file name
    train_filename = 'small_train.txt'
    valid_filename = 'small_valid.txt'
    test_filename = 'small_test.txt'
    output_train_filename = 'train_v7.json'
    output_valid_filename = 'val_v7.json'
    output_test_filename = 'test_v7.json'

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

            text=build_text_ocr_andAsr_andSum(item)
            
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

if __name__ == '__main__':
    # run_v6()
    run_v7()