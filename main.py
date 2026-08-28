import sys
from datetime import datetime
from database.connection import db_manager
from database.schema import initialize_database
from services.auth_service import AuthService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from services.report_service import ReportService
from utils.exceptions import FinanceManagerError
from utils.helpers import (
    print_header,
    print_separator,
    print_success,
    print_error,
    render_table,
    format_currency
)
from utils.validators import (
    validate_amount,
    validate_date,
    validate_choice,
    validate_required_text
)


class FinanceManagerCLI:
    def __init__(self):
        initialize_database(db_manager)

        self.auth_service = AuthService(db_manager)
        self.category_service = CategoryService(db_manager)
        self.transaction_service = TransactionService(db_manager)
        self.report_service = ReportService(db_manager)

        self.current_user = None

    def start(self):
        while True:
            if not self.current_user:
                self.show_auth_menu()
            else:
                self.show_main_menu()

    def show_auth_menu(self):
        print_header("PERSONAL FINANCE MANAGER")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print_separator()

        choice_input = input("Enter your choice: ")
        try:
            choice = validate_choice(choice_input, 1, 3)
            if choice == 1:
                self.handle_login()
            elif choice == 2:
                self.handle_register()
            elif choice == 3:
                print("\nThank you for using Personal Finance Manager. Goodbye!\n")
                sys.exit(0)
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_register(self):
        print_header("REGISTER NEW ACCOUNT")
        try:
            name = input("Name: ")
            email = input("Email: ")
            password = input("Password: ")
            confirm_password = input("Confirm password: ")

            user = self.auth_service.register_user(name, email, password, confirm_password)
            print_success(f"Registration successful! Account created for {user.name}.")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_login(self):
        print_header("USER LOGIN")
        try:
            email = input("Email: ")
            password = input("Password: ")

            user = self.auth_service.login_user(email, password)
            self.current_user = user
            print_success(f"Login successful!\n\nWelcome, {user.name}.")
        except FinanceManagerError as e:
            print_error(str(e))

    def show_main_menu(self):
        print_header("MAIN MENU")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. Search Transactions")
        print("5. Filter Transactions")
        print("6. Edit Transaction")
        print("7. Delete Transaction")
        print("8. Manage Categories")
        print("9. Financial Summary")
        print("10. Monthly Report")
        print("11. Category-wise Report")
        print("12. Export Transactions")
        print("13. Account Details")
        print("14. Logout")
        print_separator()

        choice_input = input("Enter your choice: ")
        try:
            choice = validate_choice(choice_input, 1, 14)
            if choice == 1:
                self.handle_add_transaction("income")
            elif choice == 2:
                self.handle_add_transaction("expense")
            elif choice == 3:
                self.handle_view_transactions()
            elif choice == 4:
                self.handle_search_transactions()
            elif choice == 5:
                self.handle_filter_transactions()
            elif choice == 6:
                self.handle_edit_transaction()
            elif choice == 7:
                self.handle_delete_transaction()
            elif choice == 8:
                self.handle_manage_categories()
            elif choice == 9:
                self.handle_financial_summary()
            elif choice == 10:
                self.handle_monthly_report()
            elif choice == 11:
                self.handle_category_wise_report()
            elif choice == 12:
                self.handle_export_transactions()
            elif choice == 13:
                self.handle_account_details()
            elif choice == 14:
                print_success(f"Logged out successfully. Goodbye, {self.current_user.name}!")
                self.current_user = None
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_add_transaction(self, t_type: str):
        title = "ADD INCOME" if t_type == "income" else "ADD EXPENSE"
        print_header(title)

        try:
            amount_str = input("Amount: ")
            amount = validate_amount(amount_str)

            categories = self.category_service.get_categories(self.current_user.id, category_type=t_type)
            if not categories:
                print_error(f"No {t_type} categories found. Please add a category first in Category Management.")
                return

            print("\nCategory:")
            for idx, cat in enumerate(categories, 1):
                print(f"{idx}. {cat.name}")

            cat_choice_str = input("\nChoose category: ")
            cat_choice = validate_choice(cat_choice_str, 1, len(categories))
            selected_category = categories[cat_choice - 1]

            description = input("Description: ")
            date_str = input("Date (DD-MM-YYYY): ")

            tx = self.transaction_service.add_transaction(
                user_id=self.current_user.id,
                category_id=selected_category.id,
                transaction_type=t_type,
                amount=amount,
                description=description,
                date_str=date_str
            )
            label = "Income" if t_type == "income" else "Expense"
            print_success(f"{label} added successfully!")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_view_transactions(self):
        print_header("VIEW TRANSACTIONS")
        transactions = self.transaction_service.get_transactions(self.current_user.id)
        if not transactions:
            print("\nNo transactions recorded yet.\n")
            return

        headers = ["ID", "DATE", "TYPE", "CATEGORY", "DESCRIPTION", "AMOUNT"]
        rows = []
        for tx in transactions:
            rows.append([
                tx.id,
                tx.display_date,
                tx.type.capitalize(),
                tx.category_name,
                tx.description or "-",
                format_currency(tx.amount)
            ])
        render_table(headers, rows)

    def handle_search_transactions(self):
        print_header("SEARCH TRANSACTIONS")
        keyword = input("Enter keyword: ")
        if not keyword.strip():
            print_error("Search keyword cannot be empty.")
            return

        results = self.transaction_service.search_transactions(self.current_user.id, keyword)
        print(f"\nFound {len(results)} matching transaction(s):")
        headers = ["ID", "DATE", "TYPE", "CATEGORY", "DESCRIPTION", "AMOUNT"]
        rows = []
        for tx in results:
            rows.append([
                tx.id,
                tx.display_date,
                tx.type.capitalize(),
                tx.category_name,
                tx.description or "-",
                format_currency(tx.amount)
            ])
        render_table(headers, rows)

    def handle_filter_transactions(self):
        print_header("FILTER TRANSACTIONS")
        print("Filter Options:")
        print("1. Expense")
        print("2. Income")
        print("3. All")
        
        choice_str = input("Choose: ")
        try:
            choice = validate_choice(choice_str, 1, 3)
            t_type = "expense" if choice == 1 else ("income" if choice == 2 else None)

            start_date = input("From date (DD-MM-YYYY, or press Enter to skip): ").strip() or None
            end_date = input("To date (DD-MM-YYYY, or press Enter to skip): ").strip() or None

            min_amt_str = input("Minimum amount (or press Enter to skip): ").strip()
            min_amt = validate_amount(min_amt_str) if min_amt_str else None

            max_amt_str = input("Maximum amount (or press Enter to skip): ").strip()
            max_amt = validate_amount(max_amt_str) if max_amt_str else None

            filtered = self.transaction_service.filter_transactions(
                user_id=self.current_user.id,
                transaction_type=t_type,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amt,
                max_amount=max_amt
            )

            print(f"\nFiltered Results ({len(filtered)} records found):")
            headers = ["ID", "DATE", "TYPE", "CATEGORY", "DESCRIPTION", "AMOUNT"]
            rows = []
            for tx in filtered:
                rows.append([
                    tx.id,
                    tx.display_date,
                    tx.type.capitalize(),
                    tx.category_name,
                    tx.description or "-",
                    format_currency(tx.amount)
                ])
            render_table(headers, rows)
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_edit_transaction(self):
        print_header("EDIT TRANSACTION")
        tx_id_str = input("Enter transaction ID: ")
        try:
            tx_id = int(tx_id_str.strip())
            tx = self.transaction_service.get_transaction_by_id(self.current_user.id, tx_id)

            print(f"\nCurrent Transaction Details:")
            print(f"Type: {tx.type.capitalize()} | Category: {tx.category_name} | Amount: {format_currency(tx.amount)} | Date: {tx.display_date}")

            new_amt_str = input(f"New amount (Current: {format_currency(tx.amount)}, press Enter to keep): ").strip()
            new_amount = validate_amount(new_amt_str) if new_amt_str else None

            categories = self.category_service.get_categories(self.current_user.id, category_type=tx.type)
            print("\nCategories:")
            for idx, c in enumerate(categories, 1):
                print(f"{idx}. {c.name}")
            cat_choice_str = input(f"New category choice (Current: {tx.category_name}, press Enter to keep): ").strip()
            new_cat_id = None
            if cat_choice_str:
                cat_idx = validate_choice(cat_choice_str, 1, len(categories))
                new_cat_id = categories[cat_idx - 1].id

            new_desc = input(f"New description (Current: '{tx.description}', press Enter to keep): ").strip()
            new_desc = new_desc if new_desc != "" else None

            new_date = input(f"New date (DD-MM-YYYY, Current: {tx.display_date}, press Enter to keep): ").strip() or None

            self.transaction_service.edit_transaction(
                user_id=self.current_user.id,
                transaction_id=tx_id,
                amount=new_amount,
                category_id=new_cat_id,
                description=new_desc,
                date_str=new_date
            )
            print_success("Transaction updated successfully!")
        except ValueError:
            print_error("Invalid transaction ID.")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_delete_transaction(self):
        print_header("DELETE TRANSACTION")
        tx_id_str = input("Enter transaction ID to delete: ")
        try:
            tx_id = int(tx_id_str.strip())
            tx = self.transaction_service.get_transaction_by_id(self.current_user.id, tx_id)

            print(f"\nTransaction to delete: #{tx.id} - {tx.category_name} - {format_currency(tx.amount)} ({tx.display_date})")
            print("Are you sure you want to delete this transaction?")
            print("1. Yes")
            print("2. No")
            confirm_str = input("Choice: ")
            if confirm_str.strip() == "1":
                self.transaction_service.delete_transaction(self.current_user.id, tx_id)
                print_success("Transaction deleted successfully.")
            else:
                print("\nDeletion cancelled.\n")
        except ValueError:
            print_error("Invalid transaction ID.")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_manage_categories(self):
        while True:
            print_header("CATEGORY MANAGEMENT")
            print("1. View Categories")
            print("2. Add Category")
            print("3. Rename Category")
            print("4. Delete Category")
            print("5. Back")
            print_separator()

            choice_str = input("Enter your choice: ")
            try:
                choice = validate_choice(choice_str, 1, 5)
                if choice == 1:
                    categories = self.category_service.get_categories(self.current_user.id)
                    headers = ["ID", "CATEGORY NAME", "TYPE"]
                    rows = [[c.id, c.name, c.type.capitalize()] for c in categories]
                    render_table(headers, rows)
                elif choice == 2:
                    name = input("Category Name: ")
                    t_str = input("Type (1. Income / 2. Expense): ")
                    c_choice = validate_choice(t_str, 1, 2)
                    cat_type = "income" if c_choice == 1 else "expense"
                    cat = self.category_service.add_category(self.current_user.id, name, cat_type)
                    print_success(f"Category '{cat.name}' added successfully!")
                elif choice == 3:
                    cat_id_str = input("Enter category ID to rename: ")
                    cat_id = int(cat_id_str.strip())
                    new_name = input("Enter new name: ")
                    cat = self.category_service.rename_category(self.current_user.id, cat_id, new_name)
                    print_success(f"Category renamed to '{cat.name}'.")
                elif choice == 4:
                    cat_id_str = input("Enter category ID to delete: ")
                    cat_id = int(cat_id_str.strip())
                    self.category_service.delete_category(self.current_user.id, cat_id)
                    print_success("Category deleted successfully.")
                elif choice == 5:
                    break
            except ValueError:
                print_error("Invalid input integer.")
            except FinanceManagerError as e:
                print_error(str(e))

    def handle_financial_summary(self):
        print_header("FINANCIAL SUMMARY")
        summary = self.report_service.get_financial_summary(self.current_user.id)

        print(f"Total Income       : {format_currency(summary['total_income'])}")
        print(f"Total Expenses     : {format_currency(summary['total_expenses'])}")
        print(f"Current Balance    : {format_currency(summary['balance'])}")
        print_separator()
        print(f"Number of Income Transactions  : {summary['income_count']}")
        print(f"Number of Expense Transactions : {summary['expense_count']}")
        print_separator()

    def handle_monthly_report(self):
        print_header("MONTHLY REPORT")
        try:
            m_str = input("Enter month (1-12): ")
            y_str = input("Enter year (e.g. 2026): ")
            month = validate_choice(m_str, 1, 12)
            year = int(y_str.strip())

            report = self.report_service.get_monthly_report(self.current_user.id, month, year)

            print_header(f"{report['month_name'].upper()} {report['year']} REPORT")
            print(f"Total Income       : {format_currency(report['total_income'])}")
            print(f"Total Expenses     : {format_currency(report['total_expenses'])}")
            print(f"Remaining Balance  : {format_currency(report['remaining_balance'])}")
            print_separator()
            print("Expense Breakdown")
            print_separator()

            if not report["expense_breakdown"]:
                print("No expense data recorded for this month.")
            else:
                for cat, amt in report["expense_breakdown"].items():
                    print(f"{cat.ljust(20)} {format_currency(amt)}")

            print_separator()
            print(f"Highest Spending Category : {report['highest_spending_category']}")
            print(f"Highest Single Expense    : {format_currency(report['highest_single_expense'])}")
            print(f"Average Daily Expense     : {format_currency(report['avg_daily_expense'])}")
            print_separator()
        except ValueError:
            print_error("Please enter valid numeric values for month and year.")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_category_wise_report(self):
        print_header("CATEGORY-WISE EXPENSE REPORT")
        report = self.report_service.get_category_expense_report(self.current_user.id)

        if not report["categories"]:
            print("\nNo expense records found.\n")
            return

        for item in report["categories"]:
            print(f"{item['category'].ljust(20)} {format_currency(item['amount']).ljust(15)} ({item['percentage']}%)")

        print_separator()
        print(f"Total Expenses       : {format_currency(report['total_expenses'])}")
        print_separator()
        print(f"Highest Spending Category : {report['highest_category']}")
        print(f"Lowest Spending Category  : {report['lowest_category']}")
        print_separator()

    def handle_export_transactions(self):
        print_header("EXPORT DATA")
        print("1. Export all transactions")
        print("2. Export specific month's transactions")
        print("3. Back")
        print_separator()

        choice_str = input("Choose: ")
        try:
            choice = validate_choice(choice_str, 1, 3)
            if choice == 1:
                filepath = self.report_service.export_transactions_csv(self.current_user.id)
                print_success(f"Transactions exported successfully to:\n{filepath}")
            elif choice == 2:
                m_str = input("Enter month (1-12): ")
                y_str = input("Enter year (e.g. 2026): ")
                month = validate_choice(m_str, 1, 12)
                year = int(y_str.strip())
                filepath = self.report_service.export_transactions_csv(self.current_user.id, month=month, year=year)
                print_success(f"Monthly report exported successfully to:\n{filepath}")
            elif choice == 3:
                return
        except ValueError:
            print_error("Invalid year input.")
        except FinanceManagerError as e:
            print_error(str(e))

    def handle_account_details(self):
        print_header("ACCOUNT DETAILS")
        details = self.auth_service.get_account_details(self.current_user.id)

        print(f"Name       : {details['name']}")
        print(f"Email      : {details['email']}")
        print(f"Joined On  : {details['created_at']}")
        print_separator()
        print(f"Total Transactions : {details['total_transactions']}")
        print(f"Total Income       : {format_currency(details['total_income'])}")
        print(f"Total Expenses     : {format_currency(details['total_expenses'])}")
        print(f"Net Balance        : {format_currency(details['net_balance'])}")
        print_separator()


if __name__ == "__main__":
    cli = FinanceManagerCLI()
    cli.start()
