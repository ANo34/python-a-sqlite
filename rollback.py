import sqlite3
import datetime
import pytz

db = sqlite3.connect('rollback.sqlite')
db.execute("CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY NOT NULL, balance INT NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS history (time TIMESTAMP NOT NULL, account TEXT NOT NULL, amount INT NOT NULL, PRIMARY KEY (time, account))")

class Account(object):

    @staticmethod
    def _current_time():
        return pytz.utc.localize(datetime.datetime.utcnow())

    def __init__(self, name: str, opening_balance: int = 0):
        cursor = db.execute("SELECT name, balance FROM accounts WHERE (name = ?)", (name,))
        row = cursor.fetchone()
        if row:
            self.name, self._balance = row
            print("Retrieved record for {}. ".format(self.name), end='')
        else:
            self.name = name
            self._balance = opening_balance
            cursor.execute("INSERT INTO accounts VALUES (?, ?)", (name, self._balance))
            cursor.connection.commit()
            print("Account created for {}.".format(self.name), end='')
        self.show_balance()

    def deposit(self, amount: int=0) -> float:
        if amount > 0:
            new_balance = self._balance + amount
            deposit_time = Account._current_time()
            print(deposit_time)
            db.execute("UPDATE accounts SET balance = ? WHERE (name = ?)", (new_balance, self.name))
            db.execute("INSERT INTO history VALUES (?, ?, ?) ", (deposit_time, self.name, amount))
            db.commit()
            self._balance = new_balance
            print("{:.2f} deposited".format(amount / 100))
        return self._balance / 100

    def withdraw(self, amount: int) -> float:
        if 0 < amount < self._balance:
            new_balance = self._balance - amount
            withdrawal_time = Account._current_time()
            db.execute("UPDATE accounts SET balance  = ? WHERE (name = ?)", (new_balance, self.name))
            db.execute("INSERT INTO history VALUES (?, ?, ?) ", (withdrawal_time, self.name, -amount))
            db.commit()
            self._balance = new_balance
            print("{:.2f} withdrew".format(amount / 100))
            return amount / 100
        else:
            print("The amount has to be greater than 0 and lower than your account balance")
            return 0.0

    def show_balance(self):
        print("Balance on accont {} is {:.2f}".format(self.name, self._balance / 100))

if __name__ == '__main__':
    john = Account("John")
    john.deposit(909)
    john.deposit(49)
    john.deposit(899)
    john.deposit(998)
    john.withdraw(00)
    john.withdraw(909)
    john.show_balance()

    terry = Account("Terry")
    graham = Account("Graham", 800)
    eric = Account("Eric", 900)
    tomas = Account("Tomas", 8998)

    tomas.withdraw(90)

