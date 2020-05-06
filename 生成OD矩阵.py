import pandas as pd
import warnings
warnings.filterwarnings("ignore")

tollname = pd.read_csv(r"F:\18120900\桌面\toll_id.csv")
tollname = tollname.rename({
    "tollid_x": "入口站ID",
    "tollid_y": "出口站ID"
}, axis=1).sort_values(by=["入口站ID", "出口站ID"]).reset_index(drop=True)

od_list = []

for m in range(1, 13):
    # 读取 ETC 单个文件
    # filepath = r"F:\18120900\桌面\高速公路\黑龙江资料\基础数据\2018黑龙江高速公路刷卡数据\货车原始数据\ETC180112Truck.txt"
    # 读取多个文件
    filepath = r"F:\18120900\桌面\高速公路\黑龙江资料\基础数据\2018黑龙江高速公路刷卡数据\货车原始数据\tongji18{}-Truck.txt".format(
        str(m).zfill(2))
    print("统计18{}".format(str(m).zfill(2)))

    truck = pd.read_csv(filepath, encoding="gbk")
    if truck.query("轴数 == ' '").shape[0] > 0:
        truck.loc[truck["轴数"] == ' ', "轴数"] = 0
    truck["轴数"] = truck["轴数"].astype("int")

    # 费额 != 0 表示提取得不包含绿通得数据
    truck = truck.query(
        "车种 == '货车 ' & 轴数 != 0 & 轴数 != 1 & 重量 != 0 & 里程 != 0 & 入口站ID != 0 & 费额 != 0"
    )
    truck.loc[(truck["轴数"] == 2) & (truck["重量"] <= 4500), "货车类型"] = 1
    truck.loc[(truck["轴数"] == 2) & (truck["重量"] > 4500), "货车类型"] = 2
    truck.loc[(truck["轴数"] == 3), "货车类型"] = 3
    truck.loc[(truck["轴数"] == 4), "货车类型"] = 4
    truck.loc[(truck["轴数"] == 5), "货车类型"] = 5
    truck.loc[(truck["轴数"] >= 6), "货车类型"] = 6

    # 通行量
    od = pd.pivot_table(truck, index=["入口站ID", "出口站ID"], columns=["货车类型"],
                        values="出口站", aggfunc="count").reset_index()
    od = tollname.merge(od, on=["入口站ID", "出口站ID"], how="left").set_index(["入口站ID", "出口站ID"]).fillna(0)
    od_list.append(od)
# od.to_csv(r"D:\od_ETC-2.csv", encoding="gbk")
for i in range(len(od_list) - 1):
    od_list[i + 1] = od_list[i].add(od_list[i + 1])
nod = od_list[-1].reset_index()
nod.to_csv(r"D:\od_mtc-2.csv", encoding="gbk")
