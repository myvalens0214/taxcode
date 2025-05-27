#%%
# -*- coding: utf-8-sig -*-

"""taxcalc_realestate 메인 프로그램 (2025년 기준) ver0.1 - 삼성증권 김동영"""
"""단위: 만원"""

import numpy as np
import taxcalc_broadtax as tax

# 부동산 세금 관련 상수. 2025년 기준
SINGLE_EXEMPT_LUXURY = 120000 # 1주택 비과세용 고가주택 기준액 12억원
CAPITAL_GAIN_DEDUCT = 250     # 양도소득 기본공제 250만원


def capital_gain_adj_ratio_for_single_exempt(sell_p):
    '''1주택 비과세 시의 양도차익 잔존 비율(고가주택 감안) 계산 함수. 2025년 기준
    Args:
        sell_p (float): 양도가격
    Returns:
        float: 1주택 비과세 적용 시 양도차익 잔존 비율 - 0:완전 비과세 ~ 1:완전 과세
    '''

    # 양도가격이 고가주택 기준액 이하면, 1주택 비과세 시 완전 비과세. 이상이면 비례해서 양도차익이 잔존하게 됨.
    return np.where(sell_p <= SINGLE_EXEMPT_LUXURY, 0, 1 - (SINGLE_EXEMPT_LUXURY / sell_p))


def longterm_hold_deduct_ratio_for_single_exempt(hold_year: float, resid_year: float):
    """
    1세대 1주택 장기보유특별공제율을 계산하는 함수. 2025년 기준
    Args:
        hold_year (float): 보유 기간 (년)
        resid_year (float): 거주 기간 (년)
    Returns:
        float: 공제율 - 0:공제 없음 ~ 1:공제 최대
    """

    # 보유기간 공제율 = 1년에 4%씩 증가. 단, 3년 미만은 0%임
    hold_deduct = np.minimum(np.floor(hold_year) * 0.04, 0.40)
    hold_deduct = np.where(hold_year < 3, 0, hold_deduct)

    # 거주기간 공제율 = 1년에 4%씩 증가. 단, 2년 미만은 0%임
    resid_deduct = np.minimum(np.floor(resid_year) * 0.04, 0.40)
    resid_deduct = np.where(resid_year < 2, 0, resid_deduct)

    return hold_deduct + resid_deduct


def capital_gain_for_single_house_exempt(sell_p, buy_p, holder_ratio=1, expense=0):
    '''1주택 비과세 주택 매도 시 양도차익 (고가주택, 지분율, 필요경비 감안)
    Args:
        sell_p (float): 양도가격
        buy_p (float): 취득가격
        holder_ratio (float): 주택의 지분율
        expense (float): 본인의 필요경비
    Returns:
        float: 양도차익
    '''
    # 양도차익 = (양도가격 - 취득가격 - 필요경비) * 지분율 * 1주택 비과세 적용 비율(고가주택 감안)
    return (sell_p * holder_ratio - buy_p * holder_ratio - expense) * capital_gain_adj_ratio_for_single_exempt(sell_p)


def tax_base_for_single_house_exempt(sell_p, buy_p, holder_ratio=1, expense=0, hold_year=0, resid_year=0, deduct=CAPITAL_GAIN_DEDUCT):
    '''1주택 비과세 주택 매도 시 양도소득 과세표준 (고가주택, 지분율, 필요경비, 보유기간, 거주기간, 양도소득기본공제 감안)
    Args:
        sell_p (float): 양도가격
        buy_p (float): 취득가격
        holder_ratio (float): 주택의 지분율
        expense (float): 본인의 필요경비
        hold_year (float): 보유 기간 (년)
        resid_year (float): 거주 기간 (년)
        deduct (float): 양도소득기본공제 (기본 250만원)
    Returns:
        float: 양도소득과세표준 = 양도소득금액 - 양도소득기본공제
    '''

    # 양도소득과세표준 = 양도소득금액( [양도차익-장기보유특별공제액] or [양도차익*(1-장기보유특별공제율)] ) - 양도소득기본공제
    tax_base = capital_gain_for_single_house_exempt(sell_p, buy_p, holder_ratio, expense) * \
               (1 - longterm_hold_deduct_ratio_for_single_exempt(hold_year, resid_year)) - deduct
    
    tax_base = np.where(tax_base < 0, 0, tax_base) # 양도차익이 음수인 경우 0으로 조정

    return tax_base


def capital_gain_tax_for_sing_house_exempt(sell_p, buy_p, holder_ratio=1, expense=0,hold_year=0, resid_year=0, deduct=CAPITAL_GAIN_DEDUCT):
    '''1주택 비과세 주택 매도 시 양도소득세 (고가주택, 지분율, 필요경비, 보유기간, 거주기간, 양도소득기본공제 감안)
       지방세 포함 기준임 !!!
    Args:
        sell_p (float): 양도가격
        buy_p (float): 취득가격
        holder_ratio (float): 주택의 지분율
        expense (float): 본인의 필요경비
        hold_year (float): 보유 기간 (년)
        resid_year (float): 거주 기간 (년)
        deduct (float): 양도소득기본공제 (기본 250만원)
    Returns:
        float: 양도소득세 = 양도소득과세표준 * 적용 세율 (지방세 포함 기준임 !!!)
    '''
    tax_base = tax_base_for_single_house_exempt(sell_p, buy_p, holder_ratio, expense, hold_year, resid_year, deduct) # 과세표준 계산
    gain_tax = tax.income_tax_2025(tax_base) # 세금 계산

    return gain_tax


# %%
