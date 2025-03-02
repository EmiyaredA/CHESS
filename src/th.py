import json
import os.path
import pickle
import random
from collections import defaultdict

def watch_pkl_file(file_route=None):
    if file_route is None:
        file_route = "/mnt/cache/tonghao/slns/dbProject/CHESS/data/dev/dev_databases/codebase_community/preprocessed/codebase_community_minhashes.pkl"
    # 从 .pkl 文件加载数据
    with open(file_route, "rb") as file:  # 使用二进制读模式
        loaded_data = pickle.load(file)

    print(loaded_data)


def create_dataset_by_sqlLen(dev_json, target_json, *, rate=None, file_count=None, is_random=False, seed=None):
    """

    :param dev_json: dev的json文件路径
    :param rate: 要取的比例
    :param file_count: 要取的文件数量
    :return:
    """
    with open(dev_json) as f:
        data = json.load(f)
    # 排序读取到的记录，根据每个record中的SQL字段的长度排序
    sorted_data = sorted(data, key=lambda x: len(x["SQL"]))

    if isinstance(rate, (int,float)):
        rate = max(0, min(rate, 1.0))
        file_count = int(rate * len(sorted_data))
    elif file_count:
        file_count = int(file_count)

    # 把sorted_data按file_count的数量平均分成n个部分
    chunk_size = len(sorted_data) // file_count
    remainder = len(sorted_data) % file_count

    sorted_data = [
        sorted_data[i * chunk_size + min(i, remainder):(i + 1) * chunk_size + min(i + 1, remainder)]
        for i in range(file_count)
    ]

    # 把新的记录写入到target_dir的json文件中
    all_records = []
    for i, records in enumerate(sorted_data):
        record = records[-1]
        if is_random:
            if seed:
                random.seed(seed)
            random_index = random.randint(0, len(records)-1)
            record = records[random_index]
        all_records.append(record)

    with open(target_json, "w") as f:
        json.dump(all_records, f, indent=4, ensure_ascii=False)

def create_dataset_by_difficulty(dev_json, target_json, *, rate=None, file_count=None, is_random=False, seed=None):
    """"""
    def distribute_elements(n, k):
        # 初始化结果
        result = [0] * n  # 默认所有列表分配 0 个元素

        # 如果 k < n，先分配给前 k 个列表
        if k < n:
            for i in range(k):
                result[i] = 1
        else:
            # 如果 k >= n，先每个列表分配 1 个元素
            for i in range(n):
                result[i] = 1
            
            # 将剩余的 k - n 个元素均匀分配
            remaining = k - n
            for i in range(remaining):
                result[i % n] += 1

        return result
    
    with open(dev_json) as f:
        data = json.load(f)
    # 排序读取到的记录，根据每个record中的SQL字段的长度排序
    sorted_data = sorted(data, key=lambda x: len(x["SQL"]))

    if isinstance(rate, (int,float)):
        rate = max(0, min(rate, 1.0))
        file_count = int(rate * len(sorted_data))
    elif file_count:
        file_count = int(file_count)

    # 把sorted_data按file_count的数量平均分成n个部分
    # 假设 sorted_data 是字典的列表
    grouped_data = defaultdict(list)

    for item in sorted_data:
        grouped_data[item["difficulty"]].append(item)

    # 将 grouped_data 转为普通的列表
    grouped_data = list(grouped_data.values())

    # 把新的记录写入到target_dir的json文件中
    all_records = []
    distribution = distribute_elements(len(grouped_data), file_count)
    current_index = 0

    for record, count in zip(grouped_data, distribution):
        if is_random:
            if seed: 
                random.seed(seed)
            all_records.extend(random.sample(record, count))
        else:
            all_records.extend(record[-count:])

    with open(target_json, "w") as f:
        json.dump(all_records, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    origin_dev_route = r"/mnt/cache/tonghao/slns/dbProject/CHESS/data/trueDev/dev.json"
    target_dev_route = r"/mnt/cache/tonghao/slns/dbProject/CHESS/data/dev/dev.json"
    # create_dataset_by_sqlLen(
    #     origin_dev_route,
    #     target_dev_route,
    #     is_random=True,
    #     file_count=15
    # )
    create_dataset_by_difficulty(
        origin_dev_route,
        target_dev_route,
        is_random=True,
        seed=4101,
        file_count=3
    )
