import logging

from defender_savings.services.calculator import AccountSummary

logger = logging.getLogger(__name__)

_HEADER_SEP = "-"
_COL_SEP = " | "


def _fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def print_cost_table(summaries: list[AccountSummary]) -> None:
    """Print a consolidated cost table across all cloud accounts."""
    print("\n=== Defender for Cloud - Cost Summary ===\n")

    headers = ["Cloud Account", "Module", "Tier", "Qty", "Unit Price", "Monthly", "Annual"]
    widths = [24, 30, 8, 5, 12, 12, 14]

    header_line = _COL_SEP.join(h.ljust(w) for h, w in zip(headers, widths))
    sep_line = _COL_SEP.join(_HEADER_SEP * w for w in widths)
    print(header_line)
    print(sep_line)

    grand_monthly = 0.0
    grand_annual = 0.0

    for summary in summaries:
        account_label = summary.cloud_account[:24]
        for cost in summary.costs:
            row = [
                account_label.ljust(widths[0]),
                cost.description[:widths[1]].ljust(widths[1]),
                cost.tier.ljust(widths[2]),
                str(cost.count).rjust(widths[3]),
                _fmt_usd(cost.unit_price).rjust(widths[4]),
                _fmt_usd(cost.monthly_cost).rjust(widths[5]),
                _fmt_usd(cost.annual_cost).rjust(widths[6]),
            ]
            print(_COL_SEP.join(row))
            account_label = ""  # only show account name on first row

        grand_monthly += summary.total_monthly
        grand_annual += summary.total_annual

    print(sep_line)
    total_row = [
        "TOTAL".ljust(widths[0]),
        "".ljust(widths[1]),
        "".ljust(widths[2]),
        "".rjust(widths[3]),
        "".rjust(widths[4]),
        _fmt_usd(grand_monthly).rjust(widths[5]),
        _fmt_usd(grand_annual).rjust(widths[6]),
    ]
    print(_COL_SEP.join(total_row))


def print_savings_table(summaries: list[AccountSummary]) -> None:
    """Print savings by disabling each Standard service."""
    all_savings = [s for summary in summaries for s in summary.savings]
    if not all_savings:
        print("\nNo savings opportunities found.\n")
        return

    print("\n=== Savings by Disabling Service ===\n")

    headers = ["Cloud Account", "Module", "Saving/mo", "Saving/yr"]
    widths = [24, 30, 12, 14]

    header_line = _COL_SEP.join(h.ljust(w) for h, w in zip(headers, widths))
    sep_line = _COL_SEP.join(_HEADER_SEP * w for w in widths)
    print(header_line)
    print(sep_line)

    total_saving_mo = 0.0
    total_saving_yr = 0.0

    for s in all_savings:
        row = [
            s.cloud_account[:widths[0]].ljust(widths[0]),
            s.description[:widths[1]].ljust(widths[1]),
            _fmt_usd(s.monthly_saving).rjust(widths[2]),
            _fmt_usd(s.annual_saving).rjust(widths[3]),
        ]
        print(_COL_SEP.join(row))
        total_saving_mo += s.monthly_saving
        total_saving_yr += s.annual_saving

    print(sep_line)
    total_row = [
        "TOTAL".ljust(widths[0]),
        "".ljust(widths[1]),
        _fmt_usd(total_saving_mo).rjust(widths[2]),
        _fmt_usd(total_saving_yr).rjust(widths[3]),
    ]
    print(_COL_SEP.join(total_row))
    print()
