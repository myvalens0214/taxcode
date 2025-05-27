#%%
# -*- coding: utf-8-sig -*-

"""taxcalc_broadtax 메인 프로그램 (2025년 기준) - 삼성증권 김동영"""
"""단위: 만원"""
"""모든 기준은 소득세+지방세 포함, 건보료+장기요양보험료 포함임"""

import numpy as np

# 광의의 세금 관련 상수. 2025년 기준
WITHHOLD_RATE = 0.154           # 원천징수세(소득세 14% + 지방소득세 1.4%)
EARNED_INCOME_DEDUCT = 150      # 근로소득 본인 기본공제 금액 = 150만원
FIN_INCOME_COMP_CUTOFF = 2000   # 금융소득 종합과세기준금액 = 2천만원

H_INSURE_TYPE = ['employee', 'dependent', 'self_employed']  # 건보료 가입자 유형
H_INSURE_TYPE_KOR = {'employee': '직장가입자', 'dependent': '피부양자', 'self_employed': '지역가입자'} # 가입자 한글글
H_PREMIUM_RATE = (7.09 + 0.9182) / 100  # 2025년 건강보험료율 총 8.0082%
H_EMPLOYEE_CUTOFF = 2000        # 직장가입자 건보료용 초과 기준액 = 2천만원
H_DEPENDENT_CUTOFF = 2000       # 피부양자 탈락의 소득 기준 = 2천만원

def income_tax_2025(tax_base):
    """2025년도 종합소득세 계산 일반 함수 (지방세 포함)
    Args:
        tax_base (float): 과세표준
    Returns:
        float: 종합소득세액
    """
    income_tax = np.where(
        tax_base <= 0, 0,
        np.where(tax_base <= 1400,   (0 + (tax_base - 0) * 0.06) * 1.1,
        np.where(tax_base <= 5000,   (84 + (tax_base - 1400) * 0.15) * 1.1,
        np.where(tax_base <= 8800,   (624 + (tax_base - 5000) * 0.24) * 1.1,
        np.where(tax_base <= 15000,  (1536 + (tax_base - 8800) * 0.35) * 1.1,
        np.where(tax_base <= 30000,  (3706 + (tax_base - 15000) * 0.38) * 1.1,
        np.where(tax_base <= 50000,  (9406 + (tax_base - 30000) * 0.40) * 1.1,
        np.where(tax_base <= 100000, (17406 + (tax_base - 50000) * 0.42) * 1.1,
                                     (38406 + (tax_base - 100000) * 0.45) * 1.1))))))))

    return income_tax

def withhold_tax(fin_income, tax_r=False):
    """금융소득의 원천징수세 계산 함수"""
    withhold_tax = np.maximum(fin_income, 0) * WITHHOLD_RATE

    ret = np.where(fin_income <= 0, 0,
                  withhold_tax / (fin_income if tax_r else 1))
    return ret

def comp_income_tax(comp_income, deduct=EARNED_INCOME_DEDUCT, tax_r=False):
    """기본 종합소득세(comprehensive income tax)

    Args:
        comp_income: 종합소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제 150만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        종합소득세액 또는 세율 (소득세/지방소득세 포함)
    """
    # 과세표준 = 종합소득 - 공제금액
    tax_base = comp_income - deduct

    # 종합소득세 계산 (과세표준 기준으로 계산함)
    comp_income_tax = income_tax_2025(tax_base)

    # 세금/세율
    ret = np.where(comp_income <= 0, 0,
                  comp_income_tax / (comp_income if tax_r else 1))
    return ret

def final_income_tax(fin_income, ex_fin_income, deduct=EARNED_INCOME_DEDUCT, tax_r=False):
    """최종 소득세: 금융소득과 금융외소득의 전체 세금 및 세율

    Args:
        fin_income: 금융소득금액 (만원)
        ex_fin_income: 금융외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 본인 기본공제)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        최종 소득세액 또는 세율 (소득세/지방소득세 포함)
    """
    # 금융외소득과 금융소득을 합한 소득 총액
    tot_income = ex_fin_income + fin_income

    # 62조1호 방식 세금
    tax_paragraph1 = (
        comp_income_tax(tot_income - FIN_INCOME_COMP_CUTOFF, deduct) +
        withhold_tax(FIN_INCOME_COMP_CUTOFF)
    )

    # 62조2호 방식 세금
    tax_paragraph2 = comp_income_tax(ex_fin_income, deduct) + withhold_tax(fin_income)           

    # 금융소득이 금융종합과세기준금액(2000) 이하이면 금융소득 원천징수함
    # 초과이면 금융소득초과금액과 금융소득종합과세
    tax = np.where(
        fin_income <= FIN_INCOME_COMP_CUTOFF,
        # 2천 이하여서 각각 계산하는 방식
        comp_income_tax(ex_fin_income, deduct) + withhold_tax(fin_income),
        # 2천 이상은 금융소득종합과세: 62조1호와 62조2호 금액 중 큰 값
        np.maximum(tax_paragraph1, tax_paragraph2)
    )

    # 세금/세율
    ret = np.where(tot_income <= 0, 0, tax / (tot_income if tax_r else 1))
    return ret

def income_tax_for_fin(fin_income, ex_fin_income, deduct=EARNED_INCOME_DEDUCT, tax_r=False):
    """금융소득만의 소득세금 및 세율

    Args:
        fin_income: 금융소득금액 (만원)
        ex_fin_income: 금융외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제 150만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        금융소득만의 소득세액 또는 세율 (소득세/지방소득세 포함)
    """
    # 금융소득만의 세금: 금융소득 포함한 종합 세금 - 금융소득 뺀 종합 세금
    tax = (final_income_tax(fin_income, ex_fin_income, deduct) -
           final_income_tax(0, ex_fin_income, deduct))

    # 세금/세율
    ret = np.where(fin_income <= 0, 0, tax / (fin_income if tax_r else 1))
    return ret

def income_tax_for_fin_maginal_rate(fin_income, ex_fin_income, deduct=EARNED_INCOME_DEDUCT):
    """금융소득만의 소득세 한계세율

    Args:
        fin_income: 금융소득금액 (만원)
        ex_fin_income: 금융외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제)

    Returns:
        금융소득만의 소득세 한계세율 (소득세/지방소득세 포함)
    """
    # 금융소득만의 세금: x위치와 x+1만원 위치 세금 계산
    tax_0 = (final_income_tax(fin_income, ex_fin_income, deduct) -
             final_income_tax(0, ex_fin_income, deduct))
    tax_1 = (final_income_tax(fin_income + 1, ex_fin_income, deduct) -
             final_income_tax(0, ex_fin_income, deduct))

    # 한계 세율
    ret = np.where(fin_income <= 0, 0, (tax_1 - tax_0) / 1)
    return ret

def income_health_premium(member_type, ex_salary, salary, tax_r=False):
    """가입유형별 소득의 건강보험료 전체 금액 및 세율

    Args:
        member_type: 건보료 가입자 유형
        ex_salary: 급여보수외소득금액 (만원)
        salary: 급여보수금액 (만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        건강보험료 전체 금액 또는 세율 (장기요양보험료 포함)
    """
    total_income = ex_salary + salary  # 총소득 = 급여보수외소득 + 급여보수

    # 직장가입자: 보수월액보험료는 기본 적용
    # 보수외소득월액보험료는 급여외소득 2천 초과 시에만 발생
    if member_type == 'employee':
        premium = (
            salary * H_PREMIUM_RATE +
            np.where(ex_salary <= H_EMPLOYEE_CUTOFF, 0, (ex_salary - H_EMPLOYEE_CUTOFF) * H_PREMIUM_RATE)
        )

    # 피부양자: 부담 없음
    # 단, 소득 2천만원 초과 시 피부양자 자동 탈락 후 지역가입자 전환
    elif member_type == 'dependent':
        premium = np.where(total_income <= H_DEPENDENT_CUTOFF, 0, total_income * H_PREMIUM_RATE)

    # 지역가입자: 총소득 전액에 건보요율을 곱함
    elif member_type == 'self_employed':
        premium = np.maximum(total_income, 0) * H_PREMIUM_RATE

    # 세금/세율
    ret = np.where(total_income <= 0, 0,
                  premium / (total_income if tax_r else 1))
    return ret

def h_premium_for_exsalary(member_type, ex_salary, salary, tax_r=False):
    """급여보수외소득 만의 건강보험료 및 세율

    Args:
        member_type: 건보료 가입자 유형
        ex_salary: 급여보수외소득금액 (만원)
        salary: 급여보수금액 (만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        급여보수외소득만의 건강보험료 전체 금액 또는 세율
    """
    # 금융소득만의 건보료: 금융소득 포함한 건보료 - 금융소득 뺀 건보료
    h_premium = (income_health_premium(member_type, ex_salary, salary) -
                income_health_premium(member_type, 0, salary))

    # 세금/세율
    ret = np.where(ex_salary <= 0, 0,
                  h_premium / (ex_salary if tax_r else 1))
    return ret

def broad_tax(member_type, fin_income, salary, ex_fin_salary, deduct=EARNED_INCOME_DEDUCT, tax_r=False):
    """전체 소득의 광의의 세금 및 세율

    Args:
        member_type: 건보료 가입자 유형
        fin_income: 금융소득금액 (만원)
        salary: 급여보수금액 (만원)
        ex_fin_salary: 금융및급여외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제 150만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        전체 소득의 광의의 세금(소득세+건보료) 금액 또는 세율
    """
    # 총소득 = 금융소득 + 급여보수 + 금융및급여외소득
    total_income = fin_income + salary + ex_fin_salary

    # 전체 소득의 세금 및 건보료를 합침
    tax = final_income_tax(fin_income=fin_income, ex_fin_income=(salary + ex_fin_salary), deduct=deduct) # 전체소득 세금
    premium = income_health_premium(member_type, ex_salary=(fin_income + ex_fin_salary), salary=salary) # 전체소득 건보료

    broad_tax_amount = tax + premium

    # 세금/세율
    ret = np.where(total_income <= 0, 0,
                  broad_tax_amount / (total_income if tax_r else 1))
    return ret

def broad_tax_for_fin(member_type, fin_income, salary, ex_fin_salary, deduct=EARNED_INCOME_DEDUCT, tax_r=False):
    """금융소득의 광의의 세금 및 세율

    Args:
        member_type: 건보료 가입자 유형
        fin_income: 금융소득금액 (만원)
        salary: 급여보수금액 (만원)
        ex_fin_salary: 금융및급여외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제 150만원)
        tax_r: True이면 세율, False이면 세액 반환 (기본값: False)

    Returns:
        금융소득만의 광의의 세금(소득세+건보료) 금액 또는 세율
    """
    # 광의의 세금 기준으로 계산
    broad_tax_amount = (
        broad_tax(member_type, fin_income, salary, ex_fin_salary, deduct) -
        broad_tax(member_type, 0, salary, ex_fin_salary, deduct)
    )

    # 세금/세율
    ret = np.where(fin_income <= 0, 0,
                  broad_tax_amount / (fin_income if tax_r else 1))
    return ret

def broad_tax_for_fin_maginal_rate(member_type, fin_income, salary, ex_fin_salary, deduct=EARNED_INCOME_DEDUCT):
    """금융소득만의 광의의세금 한계 세율

    Args:
        member_type: 건보료 가입자 유형
        fin_income: 금융소득금액 (만원)
        salary: 급여보수금액 (만원)
        ex_fin_salary: 금융및급여외소득금액 (만원)
        deduct: 공제금액 (만원, 기본값: 근로소득 기본공제 150만원)

    Returns:
        금융소득만의 광의의세금(소득세+건보료)의 한계세율
    """
    # x위치와 x+1만원 위치 세금 계산
    tax_0 = (
        broad_tax_for_fin(member_type, fin_income, salary, ex_fin_salary, deduct) -
        broad_tax_for_fin(member_type, 0, salary, ex_fin_salary, deduct)
    )

    tax_1 = (
        broad_tax_for_fin(member_type, fin_income + 1, salary, ex_fin_salary, deduct) -
        broad_tax_for_fin(member_type, 0, salary, ex_fin_salary, deduct)
    )

    # 한계 세율
    ret = np.where(fin_income <= 0, 0, (tax_1 - tax_0) / 1)
    return ret





# %%
