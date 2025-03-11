'''
## v5（用做content输入arg network）

因为 ocr 有很多 error，所以对所有 sample 都做了 asr

- 由于已经用 v3 做好了 rationale 生成，因此 rationale 内容沿用
- 但是在 v3 json 文件的基础上，将 content 全都改为同时使用 ocr 以及 asr。
'''
import json

def build_text(item):
    text = ''
    text += 'keywords: ' + (item.get('keywords') or 'None') + '\n'
    text += 'title: ' + (item.get('title') or 'None') + '\n'
    comments = item.get('comments')
    text += 'comments: ' + ', '.join(comments) if comments else 'None' + '\n'
    text += 'author_intro: ' + (item.get('author_intro') or 'None') + '\n'

    # use both ocr and asr anyway
    text += 'asr_result: ' + (item.get('asr') or 'None') + '\n'
    ocr_result = item.get('ocr', 'None').replace('\t', '').strip()
    text += 'ocrn_result: ' + ocr_result + '\n'

    text += 'summary: ' + (item.get('summary') or 'None') + '\n'
    return text

def content_process(input_path, output_path, data_v5_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        input = json.load(file)

        processed_v3 = []

        for sample in input:
            source_id = sample["source_id"]

            # find corresponding processed v3 sample using source_id
            the_sample_v3 = {}
            with open(input_path, 'r', encoding='utf-8') as file3:
                dataset_v3 = json.load(file3)
                for data_v3 in dataset_v3:
                    if data_v3["source_id"] == source_id:
                        the_sample_v3 = data_v3
            
            # find corresponding original v5 sample using source_id
            the_sample_v5 = {}
            with open(data_v5_path, 'r', encoding='utf-8') as file5:
                dataset_v5 = file5.readlines()

                for line in dataset_v5:
                    line = line.strip()
                    if line:  # 确保行不为空
                        data_v5 = json.loads(line)
                    if data_v5["video_id"] == source_id:
                        the_sample_v5 = data_v5
            
            # replace the 'content' value in v3(ocr or asr) with value from v5(ocr & asr)
            the_sample_v3["content"] = build_text(the_sample_v5)
            processed_v3.append(the_sample_v3)
        
        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(processed_v3, output_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    in_path = [
        "./data/split_v3/train_v3.json",
        "./data/split_v3/val_v3.json",
        "./data/split_v3/test_v3.json"
    ]
    out_path = [
        "./data/split_v3/train.json",
        "./data/split_v3/val.json",
        "./data/split_v3/test.json"
    ]
    data_v5_path = "./data/split_v3/data_complete_v5.json"
    for i, o in zip(in_path, out_path):
        content_process(i, o, data_v5_path)