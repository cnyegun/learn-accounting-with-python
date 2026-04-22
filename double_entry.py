from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

class Side(Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

@dataclass
class Entry:
    account_name: str
    side: Side
    amount: Decimal

@dataclass
class Transaction:
    description: str
    entries: list[Entry]

@dataclass
class Account:
    name: str
    account_type: AccountType
    debit_total: Decimal = field(default_factory=lambda: Decimal("0"))
    credit_total: Decimal = field(default_factory=lambda: Decimal("0"))

    def post(self, side: Side, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if side == Side.DEBIT:
            self.debit_total += amount
        else:
            self.credit_total += amount
    
    def balance(self) -> Decimal:
        match self.account_type:
            case AccountType.ASSET | AccountType.EXPENSE:
                # normal side = DEBIT
                return self.debit_total - self.credit_total
            case _:
                # normal side = CREDIT
                return self.credit_total - self.debit_total

    def balance_side(self) -> Side | None:
        if self.debit_total > self.credit_total: 
            return Side.DEBIT
        elif self.debit_total < self.credit_total:
            return Side.CREDIT
        return None
        
    def normal_side(self) -> Side:
        match self.account_type:
            case AccountType.ASSET | AccountType.EXPENSE:
                return Side.DEBIT
            case _:
                return Side.CREDIT

@dataclass
class Ledger:
    accounts: dict[str, Account] = field(default_factory=dict)
    journal: list[Transaction]   = field(default_factory=list)

    def add_account(self, name: str, account_type: AccountType) -> None:
        if name in self.accounts:
            raise ValueError(f"account is already exists: {name}")
        self.accounts[name] = Account(name, account_type)

    def get_account(self, name: str) -> Account:
        if name not in self.accounts:
            raise KeyError(f"account does not exist: {name}")
        return self.accounts[name]
    
    def post_transaction(self, tx: Transaction) -> None:
        if len(tx.entries) < 2:
            raise ValueError(f"tx need to have at least 2 entries, this: {tx.entries}")
        total_credits = Decimal("0")
        total_debits = Decimal("0")
        for entry in tx.entries:
            # validate that the account exist 
            if entry.account_name not in self.accounts:
                raise KeyError(f"account does not exist: {entry.account_name}")
            # validate the entry's amount
            if entry.amount <= 0:
                raise ValueError("amount must be positive")
            if entry.side == Side.DEBIT:
                total_debits += entry.amount
            else:
                total_credits += entry.amount
        
        if total_debits != total_credits:
            raise ValueError("unbalanced transaction")

        for entry in tx.entries:
            self.accounts[entry.account_name].post(entry.side, entry.amount)

        self.journal.append(tx)