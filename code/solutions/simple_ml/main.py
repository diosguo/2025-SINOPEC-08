from code.solutions.utils.load_data import DataLoader, RealDataLoader
import pandas as pd 
from sklearn.metrics import roc_auc_score
import random 
from loguru import logger 


def evaluate(predicitions: dict, valid_use_df: pd.DataFrame):
    """
    predicitions: order_no: predict
    """
    key_list = valid_use_df['order_no'].tolist()
    label_dict = {} 
    for idx, row in valid_use_df.iterrows():
        label_dict[row['order_no']] = 0 if pd.isna(row['coupon_code']) else 1
    predict = [] 
    label = [] 
    for k in key_list:
        if k not in predicitions:
            predict.append(0.6) 
        else:
            predict.append(predicitions[k])
        
        label.append(label_dict[k])

    score = roc_auc_score(label, predict)
    return score 

from tqdm import tqdm 
def rule_filter(valid_send_df: pd.DataFrame, valid_wallet_df: pd.DataFrame):
    # 过滤掉每个用户的无效券，获得 用户-券 的关系表
    # 首先获取用户下所有发放过的券信息
    user_coupon_dict = {}
    for idx, row in valid_send_df.iterrows():
        if row['membercode'] not in user_coupon_dict:
            user_coupon_dict[row['membercode']] = []
        user_coupon_dict[row['membercode']].append(row)
    
    # 开始过滤券
    order_valid_coupon_dict = {}

    for idx, row in tqdm(valid_wallet_df.iterrows(), total=len(valid_wallet_df), desc='规则过滤'):
        order_valid_coupon_dict[row['order_no']] = []
        coupon_list = user_coupon_dict[row['membercode']]
        valid_coupon_list = [] 
        for coupon in coupon_list:
            sale_time = row['sale_time'] # 格式类似2023/4/20 17:05 
            # sale_time转换未20230420格式
            # 处理 sale_time，确保月份和日期都是两位数
            date_part = sale_time.split(' ')[0]
            year, month, day = date_part.split('/')
            month = month.zfill(2)
            day = day.zfill(2)
            sale_time = f"{year}{month}{day}"
            send_time = str(coupon['voucherstarttime'])
            send_end_time = str(coupon['voucherendtime'])
            
            if send_time > sale_time:
                # 优惠券生效时间在订单之后，则该优惠券无效
                continue 
            if send_end_time < sale_time:
                # 结束时间在订单之前，则该优惠券无效
                continue
                
            # 省份
            coupon_province = int(coupon['marketprovince']) 
            sale_province = int(row['transactionorgcode'])
            if coupon_province != sale_province:
                # 省份不一致，则该优惠券无效
                continue
            
            # 价格， 如果门槛价格高于实际订单金额，则优惠券不可用
            top_amount = float(coupon['topamount']) / 100 # 门槛价格，原始单位是分，需要转换为元
            order_amount = float(row['tran_amt']) 
            if not pd.isna(top_amount) and top_amount > order_amount:
                # 优惠券门槛金额小于订单金额，则该优惠券无效
                # print(top_amount, order_amount)
                continue

            valid_coupon_list.append(coupon) 
        order_valid_coupon_dict[row['order_no']] = valid_coupon_list

    return order_valid_coupon_dict


def liner_perdict(train_df: pd.DataFrame, valid_df: pd.DataFrame, order_valid_coupon_dict: dict, train_order_valid_coupon_dict: dict, mode='train'):
    from sklearn.linear_model import LogisticRegression
    if mode == 'train':
        valid_df['use_coupon'] = valid_df['coupon_code'].isna()
    train_df['use_coupon'] = train_df['coupon_code'].isna()

    # 根据注册地与消费地点预测优惠券使用
    # build vocab 
    logger.info('--构建词典')
    place_vocab = {999:0} 
    for idx, row in train_df.iterrows():
        regis_place = row['attributionorgcode']
        trans_place = row['transactionorgcode']
        if pd.isna(regis_place) or pd.isna(trans_place):
            continue 
        regis_place = int(regis_place) 
        trans_place = int(trans_place) 
        
        if regis_place not in place_vocab:
            place_vocab[regis_place] = len(place_vocab) 
        if trans_place not in place_vocab: 
            place_vocab[trans_place] = len(place_vocab)  
    
    logger.info('--构建特征')
    # build one-hot feature
    features = [] 
    labels = [] 
    order_no_list = [] 
    for idx, row in train_df.iterrows():
        order_no = row['order_no']
        if order_no not in train_order_valid_coupon_dict or len(train_order_valid_coupon_dict[order_no]) == 0:
            continue
        valid_coupon_number = len(train_order_valid_coupon_dict[order_no]) 
        regis_place = row['attributionorgcode']
        trans_place = row['transactionorgcode']
        if pd.isna(regis_place):
            regis_place = 999 
        if pd.isna(trans_place):
            trans_place = 999

        regis_place = int(regis_place) 
        trans_place = int(trans_place) 

        regis_feature = [0] * len(place_vocab)
        trans_feature = [0] * len(place_vocab) 
        regis_feature[place_vocab[regis_place]] = 1 
        trans_feature[place_vocab[trans_place]] = 1 
        same_feature = 1 if regis_place == trans_place else 0  

        label = 1 if row['use_coupon'] else 0 
        features.append(regis_feature+trans_feature+[same_feature, valid_coupon_number]) 
        labels.append(label)  
        order_no_list.append(order_no)
    logger.info('--训练模型')
    model = LogisticRegression()
    model.fit(features, labels)
    train_predicts = model.predict_proba(features) 
    train_predicts = [x[1] for x in train_predicts]
    train_auc = roc_auc_score(labels, train_predicts)
    logger.info(f'--训练集AUC: {train_auc}')

    # build one-hot feature
    logger.info('--构建特征')
    features = [] 
    labels = []
    order_no_list = [] 
    for idx, row in valid_df.iterrows():
        order_no = row['order_no']
        if order_no not in order_valid_coupon_dict or len(order_valid_coupon_dict[order_no]) == 0:
            continue
        valid_coupon_number = len(order_valid_coupon_dict[order_no]) 
        regis_place = row['attributionorgcode']
        trans_place = row['transactionorgcode']
        if pd.isna(regis_place):
            regis_place = 999 
        if pd.isna(trans_place):
            trans_place = 999

        regis_place = int(regis_place)
        trans_place = int(trans_place)

        regis_feature = [0] * len(place_vocab)
        trans_feature = [0] * len(place_vocab) 
        regis_feature[place_vocab[regis_place]] = 1 
        trans_feature[place_vocab[trans_place]] = 1 
        same_feature = 1 if regis_place == trans_place else 0  
        if mode == 'train':
            label = 1 if row['use_coupon'] else 0 
            labels.append(label)  
        features.append(regis_feature+trans_feature+[same_feature, valid_coupon_number]) 
        order_no_list.append(order_no)

    logger.info('--预测')
    predicts = model.predict_proba(features)
    if mode == 'train':
        valid_predicts = [x[1] for x in predicts]
        valid_auc = roc_auc_score(labels, valid_predicts)
        logger.info(f'--验证集AUC: {valid_auc}')
    probs = {}
    for order_no, p in zip(order_no_list, predicts):
        probs[order_no] = p[0]
    return probs 


def main(mode='train'):
    if mode == 'train':
        logger.info('加载数据')
        data_loader = DataLoader('../../../data/train_data')
        
        
        key_list = data_loader.valid_wallet_df['order_no'].tolist() 
        random_result = {}

        logger.info('规则过滤订单下的优惠券')
        order_valid_coupon_dict = rule_filter(data_loader.valid_send_df, data_loader.valid_wallet_df)
        logger.info(f'规则过滤后订单数: {len([x for x in order_valid_coupon_dict.values() if len(x) > 0])}')
        train_order_valid_coupon_dict = rule_filter(data_loader.train_send_df, data_loader.train_wallet_df)
        logger.info('线性模型预测') 
        probs_dict = liner_perdict(data_loader.train_wallet_df, data_loader.valid_wallet_df, order_valid_coupon_dict, train_order_valid_coupon_dict, mode=mode)
        for k in key_list:
            if k in probs_dict:
                random_result[k] = probs_dict[k]
            else:
                random_result[k] = random.random()
            if k in order_valid_coupon_dict and len(order_valid_coupon_dict[k]) == 0:
                random_result[k] = 0

        # 验证分数
        print(evaluate(random_result, data_loader.valid_wallet_df))
    else:
        logger.info('加载数据')
        data_loader = RealDataLoader()
        key_list = data_loader.valid_wallet_df['order_no'].tolist() 
        random_result = {}

        logger.info('规则过滤订单下的优惠券')
        order_valid_coupon_dict = rule_filter(data_loader.valid_send_df, data_loader.valid_wallet_df)
        logger.info(f'规则过滤后订单数: {len([x for x in order_valid_coupon_dict.values() if len(x) > 0])}')
        train_order_valid_coupon_dict = rule_filter(data_loader.train_send_df, data_loader.train_wallet_df)
        logger.info('线性模型预测') 
        probs_dict = liner_perdict(data_loader.train_wallet_df, data_loader.valid_wallet_df, order_valid_coupon_dict, train_order_valid_coupon_dict, mode=mode)
        for k in key_list:
            if k in probs_dict:
                random_result[k] = probs_dict[k]
            else:
                random_result[k] = random.random()
            if k in order_valid_coupon_dict and len(order_valid_coupon_dict[k]) == 0:
                random_result[k] = 0

        output = [] 
        for k, v in random_result.items():
            output.append([k, v]) 
        df = pd.DataFrame(output, columns=['id', 'predict']) 
        df.to_csv('./rule_filter_result_202508290038.csv', index=False)

if __name__ == '__main__':
    main('valid')