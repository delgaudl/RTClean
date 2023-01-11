import pandas as pd
import sys, os

def checkForOutlier(value, value_sec):
    return abs(float(value) - float(value_sec)) > 3.3

df1 = pd.read_csv(os.path.join(sys.path[0], "iot-dboost-dirty-2.csv"), header=0)
df2 = pd.read_csv(os.path.join(sys.path[0], "iot-dboost-clean-1.csv"), header=0)

true_errors = [1251, 8367, 2102, 8345, 5948, 5729, 2507, 2607, 1270, 765, 3081, 1695, 1015, 7750, 6608, 3242, 6285, 1354, 5483, 5593, 3592, 1895, 5118, 6250, 7389, 1519, 1301, 4187, 2496, 2452, 1306, 7421, 443, 2736, 5324, 4642, 2655, 2177, 8497, 8483, 5377, 7626, 5650, 7788, 3939, 3176, 3146, 7474, 7078, 596, 6539, 220, 5062, 6904, 548, 4416, 4371, 4191, 3596, 1464, 1126, 5004, 8384, 1139, 2663, 2134, 6260, 3304, 8163, 4631, 3877, 4456, 4171, 167, 8093, 8174, 6577, 4059, 3002, 1916, 6495, 7295, 58, 5392, 206]
all = len(true_errors)
true_pos = 0 
false_pos = 0
false_neg = 0
true_neg = 0

for row in df1.iterrows():
    list = df2[df2.time == row[1].time]
    if (len(list) == 0): continue
    if (checkForOutlier(list.iloc[0][1], row[1].value)):
        #print(row[1].time, row[1].value)
        if (row[0] in true_errors):
            true_pos += 1
        else:
            false_pos += 1
    else:
        if (row[0] in true_errors):
            false_neg += 1
        else:
            true_neg += 1

precision = true_pos / (true_pos + false_pos)
recall = true_pos / (true_pos + false_neg)
f1 = (2*true_pos / (2*true_pos + false_pos + false_neg))

print(f"TP: {true_pos}, FP: {false_pos}, FN: {false_neg}, TN: {true_neg}")
print(f"Prec: {precision}, Recall: {recall}, F1-score: {f1}")