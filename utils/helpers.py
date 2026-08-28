from typing import List, Dict, Any


def format_currency(amount: float) -> str:
    val_str = f"{amount:,.2f}"
    if val_str.endswith('.00'):
        val_str = f"{int(amount):,}"
    return f"₹{val_str}"


def print_header(title: str, width: int = 68) -> None:
    print("=" * width)
    print(title.center(width))
    print("=" * width)


def print_separator(width: int = 68) -> None:
    print("-" * width)


def print_success(message: str) -> None:
    print(f"\n✓ {message}\n")


def print_error(message: str) -> None:
    print(f"\n✗ {message}\n")


def render_table(headers: List[str], rows: List[List[Any]], col_widths: List[int] = None) -> None:
    if not rows:
        print("\nNo records found.\n")
        return

    if not col_widths:
        col_widths = []
        for i in range(len(headers)):
            max_len = len(headers[i])
            for row in rows:
                cell_len = len(str(row[i])) if i < len(row) else 0
                if cell_len > max_len:
                    max_len = cell_len
            col_widths.append(max_len + 2)

    total_width = sum(col_widths) + len(col_widths) + 1

    border = "=" * total_width

    print(border)
    header_line = "|"
    for i, h in enumerate(headers):
        header_line += f" {str(h).ljust(col_widths[i] - 1)}|"
    print(header_line)
    print(border)

    for row in rows:
        row_line = "|"
        for i, val in enumerate(row):
            w = col_widths[i]
            val_str = str(val)
            row_line += f" {val_str.ljust(w - 1)}|"
        print(row_line)

    print(border)
