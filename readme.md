# 竞赛项目-2025-中国石化-

[竞赛地址:https://aicup.sinopec.com/competition/SINOPEC-08/make-submission/](https://aicup.sinopec.com/competition/SINOPEC-08/make-submission/)

# 数据说明

数据说明  
本次比赛的数据已全部进行脱敏处理。

1. 钱包交易数据表(cust_wallet_detail.csv)

| 字段名称 | 字段含义 |
| ---- | ---- | 
| order_no/external_order_no | 交易的唯一ID。order_no是系统内部的订单号，external_order_no是关联的第三方或支付平台的订单号。 |
| user_id | 经过脱敏处理的用户唯一编号。 |
| membercode | 会员编码,与发券用券表客户进行关联 |
| station_code / station_name | 交易发生的加油站的唯一编码和名称 | 
| sale_time | 交易发生的精确到秒的时间戳 | 
| tran_amt / receivable_amt | tran_amt是商品原价总额；receivable_amt是应收总额。 |
| discounts_amt / point_amt / coupon_amt | 分别记录了通用折扣、积分兑换和优惠券带来的优惠金额 |
| attributionorgcode / transactionorgcode | 用户注册省市与消费省市编码 |
| Coupon_code | 核销电子券编码,可与优惠券使用电子券编码关联 |

2. 优惠券使用(cust_coupon_detail_used.csv)

| 字段名称 | 字段含义 |
| ---- | ---- |
| marketcode | 营销活动编码 |
| marketrulenumber | 活动细则编号（营销规则编码，细则编码对应多个规则编码） |
| voucherrulecode | 电子券规则编码 |
| vouchercode | 电子券编号 |
| vouchertype | 电子券类型（C01：现金券，C02：满抵券，C04：折扣券） |
| vouchername | 电子券中文名称 |
| transtime | 电子券使用时间，格式：yyyy-MM-dd HH:mm:ss |
| provinceCode | 电子券所属省份 |
| membercode | 会员编码（与发券、交易数据进行关联） |
| channel | 电子券实际使用渠道 |
| netCode | 电子券实际使用网点 |
| couponUseMoney | 电子券使用金额，单位分 |

3. 优惠券发放(cust_coupon_detail_send.csv)

| 字段名称 | 字段含义 |
| ---- | ---- |
| marketcode | 营销活动编码 |
| marketrulenumber | 活动细则编号（营销规则编码，细则编码对应多个规则编码） |
| membercode | 会员编码（与用券、流水表客户进行关联） |
| marketprovince | 活动省份 |
| voucherruleCode | 电子券规则编码 |
| voucherrulename | 电子券规则名称 |
| voucherstarttime | 电子券生效时间 |
| voucherendTime | 电子券失效时间 |
| vouchertype | 电子券类型（C01：现金券，C02：满抵券，C04：折扣券） |
| fulltype | 电子券小类型（如为C02满抵券时必填，01：满额抵，02：满额赠） |
| usechannel | 电子券使用渠道 |
| cashvalue | 电子券面额，单位分 |
| topamount | 电子券满额（满抵券时必填，满足金额条件，单位分） |
| endnumber | 电子券剩余数量 |

其中以_train为尾缀的文件对应训练集文件，_validation尾缀的文件对应验证集文件。  
cust_wallet_detail_validation_without_truth.csv 为初赛待预测的用户数据，文件格式与train相同但是不提供用户是否使用优惠券相关的数据。

4. 提交文件 sample_submission.csv  
规定了初赛提交以及模型输出文件的格式。包含id与predict。  
其中:

id为交易数据表中对应的订单号order_no。  
predict为预测该用户响应营销事件的可能性的AUC结果值。