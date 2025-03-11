# import json
# import random

# '''
# 弃用
# '''

# # 从 JSON 文件读取数据
# with open('./data/fakeSV_for_ARG.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# # 筛选数据，只保留 cs_pred 和 td_pred 为 'fake' 或 'real' 的条目
# filtered_data = [
#     item for item in data
#     if item.get('td_pred') in ['fake', 'real'] and item.get('cs_pred') in ['fake', 'real']
# ]

# # 随机打乱数据
# random.shuffle(filtered_data)

# # 计算分割索引
# total = len(filtered_data)
# train_split = int(total * 0.6)
# val_split = int(total * 0.8)
# print("# Total data:", total)
# print("# Training data:", train_split)
# print("# Val / Test data:", val_split - train_split)

# # 分割数据
# train_data = filtered_data[:train_split]
# val_data = filtered_data[train_split:val_split]
# test_data = filtered_data[val_split:]

# # 修改 split 属性
# for item in train_data:
#     item['split'] = 'train'
# for item in val_data:
#     item['split'] = 'val'
# for item in test_data:
#     item['split'] = 'test'

# # 保存到文件
# with open('./data/split/train.json', 'w', encoding='utf-8') as f:
#     json.dump(train_data, f, ensure_ascii=False, indent=4)

# with open('./data/split/val.json', 'w', encoding='utf-8') as f:
#     json.dump(val_data, f, ensure_ascii=False, indent=4)

# with open('./data/split/test.json', 'w', encoding='utf-8') as f:
#     json.dump(test_data, f, ensure_ascii=False, indent=4)

# print("数据分割完成，已保存为 train.json, val.json 和 test.json。")