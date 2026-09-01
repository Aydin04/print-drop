"""
HPP & Selling Price Calculation Engine for Aydin Print
Ported from auto-print (PrintCalculations.kt)
"""
import math

def calculate_cut_fits_per_page(master_w_cm, master_h_cm, cut_w_cm, cut_h_cm, spacing_margin_cm=0.2):
    """
    Calculates how many cut photos/items fit into a master paper sheet.
    Evaluates both orientations (portrait & landscape) and returns the maximum fit.
    """
    if cut_w_cm <= 0 or cut_h_cm <= 0 or master_w_cm <= 0 or master_h_cm <= 0:
        return 1
    if cut_w_cm >= master_w_cm and cut_h_cm >= master_h_cm:
        return 1

    eff_mw = master_w_cm + spacing_margin_cm
    eff_mh = master_h_cm + spacing_margin_cm
    eff_cw = cut_w_cm + spacing_margin_cm
    eff_ch = cut_h_cm + spacing_margin_cm

    cols_a = int(math.floor(eff_mw / eff_cw))
    rows_a = int(math.floor(eff_mh / eff_ch))
    fit_a = max(1, cols_a * rows_a)

    cols_b = int(math.floor(eff_mw / eff_ch))
    rows_b = int(math.floor(eff_mh / eff_cw))
    fit_b = max(1, cols_b * rows_b)

    return max(fit_a, fit_b)


def calculate_hpp(
    pack_price: float,
    sheets_per_pack: int,
    total_quantity_ordered: int,
    cut_fits_per_page: int = 1,
    avg_ink_price_per_ml: float = 1200.0,
    ml_ink_per_sheet: float = 0.4,
    printer_watt: float = 16.0,
    print_time_seconds_per_page: float = 15.0,
    electricity_rate_per_kwh: float = 1500.0,
    printer_purchase_price: float = 3200000.0,
    estimated_page_capacity: int = 50000,
    extra_costs: float = 0.0,
    accessory_cost_total: float = 0.0,
    depreciation_multiplier: float = 1.0,
    duplex: bool = False
):
    """
    Comprehensive HPP calculation considering Paper, Ink, Electricity,
    Depreciation, Extra Costs, and Accessories.
    """
    safe_sheets_per_pack = max(1, sheets_per_pack)
    safe_cut_fits = max(1, cut_fits_per_page)

    # Master sheets needed to print total_quantity_ordered
    master_sheets_needed = max(1, math.ceil(total_quantity_ordered / safe_cut_fits))
    total_printed_sides = master_sheets_needed * 2 if duplex else master_sheets_needed

    # 1. Paper cost
    paper_cost_per_sheet = pack_price / safe_sheets_per_pack
    paper_cost_total = master_sheets_needed * paper_cost_per_sheet

    # 2. Ink cost
    ink_cost_per_side = ml_ink_per_sheet * avg_ink_price_per_ml
    ink_cost_total = total_printed_sides * ink_cost_per_side

    # 3. Electricity cost
    hours_per_side = print_time_seconds_per_page / 3600.0
    electricity_cost_per_side = (printer_watt / 1000.0) * hours_per_side * electricity_rate_per_kwh
    electricity_cost_total = total_printed_sides * electricity_cost_per_side

    # 4. Depreciation cost
    safe_capacity = max(1, estimated_page_capacity)
    depreciation_cost_per_side = (printer_purchase_price / safe_capacity) * depreciation_multiplier
    depreciation_cost_total = total_printed_sides * depreciation_cost_per_side

    # 5. Total HPP
    hpp_total = (
        paper_cost_total
        + ink_cost_total
        + electricity_cost_total
        + depreciation_cost_total
        + extra_costs
        + accessory_cost_total
    )
    hpp_per_unit = hpp_total / max(1, total_quantity_ordered)

    return {
        "paper_cost_total": round(paper_cost_total, 2),
        "ink_cost_total": round(ink_cost_total, 2),
        "electricity_cost_total": round(electricity_cost_total, 2),
        "depreciation_cost_total": round(depreciation_cost_total, 2),
        "extra_costs": round(extra_costs, 2),
        "accessory_cost_total": round(accessory_cost_total, 2),
        "hpp_total": round(hpp_total, 2),
        "hpp_per_unit": round(hpp_per_unit, 2),
        "paper_cost_per_sheet": round(paper_cost_per_sheet, 2),
        "ink_cost_per_sheet": round(ink_cost_per_side, 2),
        "electricity_cost_per_sheet": round(electricity_cost_per_side, 2),
        "depreciation_cost_per_sheet": round(depreciation_cost_per_side, 2),
        "total_master_sheets_needed": master_sheets_needed
    }


def calculate_selling_price(
    hpp_total: float,
    hpp_per_unit: float,
    quantity: int,
    margin_percent: float = 40.0,
    margin_type: str = "MARKUP",
    min_profit_per_sheet: float = 0.0,
    total_sheets: int = 1
):
    """
    Calculates final selling price with either Markup, Gross Margin, or Fixed Profit per Sheet/Pcs.
    """
    safe_quantity = max(1, quantity)
    margin_type = (margin_type or "MARKUP").upper()

    if margin_type == "GROSS_MARGIN":
        if margin_percent >= 100.0:
            selling_price_total = hpp_total * 2.0
        else:
            selling_price_total = hpp_total / (1.0 - (margin_percent / 100.0))
    else:
        # Default MARKUP
        selling_price_total = hpp_total * (1.0 + (margin_percent / 100.0))

    # Apply minimum profit per sheet if configured
    if min_profit_per_sheet > 0:
        min_total_profit = min_profit_per_sheet * max(1, total_sheets)
        calculated_profit = selling_price_total - hpp_total
        if calculated_profit < min_total_profit:
            selling_price_total = hpp_total + min_total_profit

    selling_price_per_unit = selling_price_total / safe_quantity
    profit_total = selling_price_total - hpp_total
    profit_per_unit = profit_total / safe_quantity

    return {
        "selling_price_total": round(selling_price_total, 2),
        "selling_price_per_unit": round(selling_price_per_unit, 2),
        "profit_total": round(profit_total, 2),
        "profit_per_unit": round(profit_per_unit, 2)
    }


def round_to_nearest(amount: float, nearest: float = 500.0) -> int:
    """Rounds amount up to the nearest denomination (e.g. 500, 1000)."""
    if nearest <= 0:
        return int(amount)
    return int(math.ceil(amount / nearest) * nearest)
