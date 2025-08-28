# 将数据进行拆分
import pandas as pd 
import numpy as np

np.random.seed(42)

raw_train_send_df = pd.read_csv('../../../data/extracted/cust_coupon_detail_send_train.csv')
raw_train_use_df = pd.read_csv('../../../data/extracted/cust_coupon_detail_used_train.csv')
raw_train_wallet_df = pd.read_csv('../../../data/extracted/cust_wallet_detail_train.csv')

# 将raw_train_user_df按照membercode分组，然后按照8:2的比例划分为train_use_df和valid_use_df
# 先获取所有membercode
all_membercodes = raw_train_send_df['membercode'].unique()
# 随机抽取80%的membercode作为训练，其余20%作为验证
train_membercodes = np.random.choice(all_membercodes, size=int(0.8 * len(all_membercodes)), replace=False)

# 优惠券使用数据
train_use_df = raw_train_use_df[raw_train_use_df['membercode'].isin(train_membercodes)].reset_index(drop=True)
# 获取train_use_df中membercode不在raw_train_use_df中数据
valid_use_df = raw_train_use_df[~raw_train_use_df['membercode'].isin(train_use_df['membercode'])].reset_index(drop=True) 

# 优惠券发放数据
train_send_df = raw_train_send_df[raw_train_send_df['membercode'].isin(train_membercodes)].reset_index(drop=True) 
valid_send_df = raw_train_send_df[~raw_train_send_df['membercode'].isin(train_membercodes)].reset_index(drop=True) 

# 钱包数据
train_wallet_df = raw_train_wallet_df[raw_train_wallet_df['membercode'].isin(train_membercodes)].reset_index(drop=True) 
valid_wallet_df = raw_train_wallet_df[~raw_train_wallet_df['membercode'].isin(train_membercodes)].reset_index(drop=True) 

# 保存数据
train_use_df.to_csv('../../../data/train_data/train_use.csv', index=False)
valid_use_df.to_csv('../../../data/train_data/valid_use.csv', index=False)
train_send_df.to_csv('../../../data/train_data/train_send.csv', index=False)
valid_send_df.to_csv('../../../data/train_data/valid_send.csv', index=False)
train_wallet_df.to_csv('../../../data/train_data/train_wallet.csv', index=False)
valid_wallet_df.to_csv('../../../data/train_data/valid_wallet.csv', index=False)
