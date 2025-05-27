#%%
# -*- coding: utf-8-sig -*-

"""taxcalc_broadtax 민감도 분석 샘플 - 삼성증권 김동영"""
"""단위: 만원"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
import taxcalc_broadtax as tax

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지
plt.rcParams['axes.grid'] = True  # 격자 표시 여부


# analysis 1
story = '동일 소득의 원천징수세율과 종합소득세율 비교'
incomes = np.linspace(1, 20000, 500)  # 1만원 ~ 2억원 

plt.plot(incomes, tax.withhold_tax(incomes, tax_r=True), label='금융소득 가정 시의 원천징수세율')
plt.plot(incomes, tax.comp_income_tax(incomes, tax_r=True), label='종합소득 가정 시의 종합소득세율')
plt.title(story)
plt.xlabel('소득 (만원)')
plt.ylabel('세율 (%)')
plt.legend()
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.gca().yaxis.set_major_formatter(PercentFormatter(1, 0))
plt.show()


# analysis 2
story = '금융/금융외 소득이 있을 때의 금융소득세율 변화'
other_incomes = np.linspace(16000, 0, 9)  # 금융외소득 1.6억원 ~ 0원
fin_incomes = np.linspace(1, 10000, 500)  # 금융소득 1만원 ~ 1억원 

for other_income in other_incomes:
    label = f'금융외소득 {other_income:,.0f}'
    plt.plot(fin_incomes, tax.income_tax_for_fin(fin_incomes, ex_fin_income=other_income, tax_r=True),
              linestyle='dashed', label=label)

plt.title(story)
plt.xlabel('금융소득 (만원)')
plt.ylabel('금융소득세율 (%)')
plt.legend()
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.gca().yaxis.set_major_formatter(PercentFormatter(1, 0))
plt.show()


# analysis 3
story = '금융/금융외 소득이 있을 때의 금융소득세율 변화 3D 그래프'
fin_incomes = np.linspace(1,10000, 100)  # 금융소득 1만원 ~ 1억원 
other_incomes = np.linspace(1,10000, 100)  # 금융외소득 1만원 ~ 1억원

X, Y = np.meshgrid(fin_incomes, other_incomes)
Z = tax.income_tax_for_fin(fin_income=X, ex_fin_income=Y, tax_r=True)  # 금융소득세율 (X축만 포커스)

fig = plt.figure(figsize=(7, 8))
ax = fig.add_subplot(projection='3d')
ax.plot_surface(X, Y, Z, cmap='Spectral', edgecolor='lightgray', linewidth=0.1)
plt.title(story)
ax.set_xlabel('금융소득 (만원)', color='blue')
ax.set_ylabel('(금융외소득 (만원))')
ax.set_zlabel('금융소득세율', color='blue', labelpad=-26)
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.zaxis.set_major_formatter(PercentFormatter(1, 0))
plt.show()


# analysis 4
story = '급여외 소득에 대한 건강보험료율의 변화'

fin_incomes = np.linspace(1, 8000, 500)

for key, value in tax.H_INSURE_TYPE_KOR.items():
    plt.plot(fin_incomes, tax.h_premium_for_exsalary(key, ex_salary=fin_incomes, salary=0, tax_r=True), 
             linestyle='dashed', label=value)

plt.title(story)
plt.xlabel('급여 외 소득 (만원)')
plt.ylabel('건강보험료율')
plt.legend()
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
plt.show()


# analysis 5
story = '금융소득의 "광의의 세율" 3D 그래프 (직장가입자 및 지역가입자 비교)' +\
        '\n\n* 아래 커브: 직장가입자, 위 커브: 지역가입자'

def plot_surf(X, Y, Z, **kwargs):
    ax.plot_surface(X, Y, Z, cmap='Spectral', edgecolor='lightgray', linewidth=0.1, **kwargs)

fin_incomes = np.linspace(1, 20000, 100)
other_incomes = np.linspace(1, 20000, 100)
X, Y = np.meshgrid(fin_incomes, other_incomes)

Z = tax.broad_tax_for_fin('employee', fin_income=X, salary=Y, ex_fin_salary=0, tax_r=True)
Z1 = tax.broad_tax_for_fin('self_employed', fin_income=X, salary=0, ex_fin_salary=Y, tax_r=True)

fig = plt.figure(figsize=(7, 8))
ax = fig.add_subplot(projection='3d')
plot_surf(X, Y, Z)
plot_surf(X, Y, Z1)
ax.set_title(story)
ax.set_xlabel('금융소득 (만원)', color='blue')
ax.set_ylabel('(금융외소득 (만원))')
ax.set_zlabel('금융소득의 광의세율 ', color='blue', labelpad=-26)
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.zaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
plt.show()


# %%
