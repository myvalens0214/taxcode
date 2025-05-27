#%%
# -*- coding: utf-8-sig -*-

"""taxcalc_realestate 민감도 분석 샘플 - 삼성증권 김동영"""
"""단위: 만원"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
import taxcalc_realestate as estate

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지
plt.rcParams['axes.grid'] = True  # 격자 표시 여부

# analysis 1
story = '양도가액에 따른, 1주택 비과세 적용 시 양도차익 잔존 비율 (고가주택 감안)'
sell_ps = np.linspace(1, 400000, 1000)
plt.plot(sell_ps, estate.capital_gain_adj_ratio_for_single_exempt(sell_ps), label='1주택 비과세 적용 시 양도차익 잔존 비율')
plt.title(story)
plt.xlabel('매도금액 (만원)')
plt.ylabel('잔존비율 (%)')
plt.legend()
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.gca().yaxis.set_major_formatter(PercentFormatter(1, 0))
plt.show()


# analysis 2
# 부동산 양도소득세 계산 예제
story = '예시: 양도가 20억원, 취득가 10억원, 지분율 50%, 필요경비 2천만원, 보유 5년, 거주 3년, 기본공제 250만원인' +\
        '\n      1주택 비과세 대상 주택 매도 시의 양도세 계산'
print(story)
print('양도세: ', np.round(estate.capital_gain_tax_for_sing_house_exempt(200000, 100000, 0.5, 2000, 5, 3), 2), '만원')


# analysis 3
# 부동산 양도소득세 민감도 분석 예제
story = '[ 부동산 양도소득세 민감도 분석 예제 ]' + \
        '\n 1주택 비과세 대상 주택 매도: 취득가액 10억원, 지분율 50%, 본인 필요경비 2천만원 가정,' + \
        '\n 양도가액 11억원 ~ 20억원, 보유/거주기간 1~10년에 따른, 양도세 민감도 분석'
years = range(1, 11)
sell_ps = np.linspace(110000, 200000, 500)

for year in years:
    label = f'보유/거주기간 {year}년'
    plt.plot(sell_ps, estate.capital_gain_tax_for_sing_house_exempt(sell_ps, 100000, 0.5, 2000, year, year),
              linestyle='dashed', label=label)

plt.title(story)
plt.xlabel('매도금액 (만원)')
plt.ylabel('양도세 (만원)')
plt.legend()
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.show()


# %%
