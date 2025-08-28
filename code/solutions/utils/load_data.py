import pandas as pd 
import os 


class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path
        self.train_use_df = pd.read_csv(os.path.join(self.data_path, 'train_use.csv'))
        self.valid_use_df = pd.read_csv(os.path.join(self.data_path, 'valid_use.csv'))
        self.train_send_df = pd.read_csv(os.path.join(self.data_path, 'train_send.csv'))
        self.valid_send_df = pd.read_csv(os.path.join(self.data_path, 'valid_send.csv'))
        self.train_wallet_df = pd.read_csv(os.path.join(self.data_path, 'train_wallet.csv'))
        self.valid_wallet_df = pd.read_csv(os.path.join(self.data_path, 'valid_wallet.csv'))


class RealDataLoader:
    def __init__(self) -> None:
        self.data_path = 'D:\\自己\\Competition\\2025-SINOPEC-08\\data\\extracted'
        # self.train_use_df = pd.read_csv(os.path.join(self.data_path, 'train_use.csv'))
        # self.valid_use_df = pd.read_csv(os.path.join(self.data_path, 'valid_use.csv'))
        self.train_send_df = pd.read_csv(os.path.join(self.data_path, 'cust_coupon_detail_send_train.csv'))
        self.valid_send_df = pd.read_csv(os.path.join(self.data_path, 'cust_coupon_detail_send_validation.csv'))
        self.train_wallet_df = pd.read_csv(os.path.join(self.data_path, 'cust_wallet_detail_train.csv'))
        self.valid_wallet_df = pd.read_csv(os.path.join(self.data_path, 'cust_wallet_detail_validation_without_truth.csv'))