# Generating plausible Russian requisites (test data)

Use when a contract needs ОГРНИП, ИНН, a settlement account or a postal index that the source document does not provide. Values must pass the real check-digit algorithms, otherwise anyone who verifies them sees a fake instantly.

## ОГРНИП — 15 digits

Structure: `3` (ИП) + `YY` (registration year) + `RR` (region) + `NN` (two-digit tax-office part) + 7 digits + check.

```python
def ogrnip(base14):          # 14 chars, e.g. '3247719123456 7' -> 15
    return base14 + str((int(base14) % 13) % 10)
```

The year inside the number must match the registration date printed next to it (`324…` ⇒ 2024).

## ИНН — 12 digits for an individual / ИП

First 4 digits = tax-office code (take it from the address: Moscow streets resolve to codes like `7701`, `7719`), then 6 digits, then two check digits.

```python
def inn12(base10):
    n = [int(c) for c in base10]
    w1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    c11 = sum(a * b for a, b in zip(n, w1)) % 11 % 10
    w2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    c12 = sum(a * b for a, b in zip(n + [c11], w2)) % 11 % 10
    return base10 + str(c11) + str(c12)
```

## Settlement account — 20 digits, control key at position 9

Structure: `40802` (ИП current account) + `810` (RUB) + key + 4-digit branch + 7-digit number.
The key is computed over a 23-character string: last 3 digits of БИК + the account with the key position zeroed.

```python
def acc_key(acc20, bik):
    s = bik[-3:] + acc20[:8] + "0" + acc20[9:]
    tot = sum(int(ch) * [3, 1, 7][i % 3] for i, ch in enumerate(s))
    return 0 if tot % 10 == 0 else 10 - tot % 10
```

Validate the implementation against a known-good account before emitting one: `40802810638000507759` with БИК `044525225` must yield `6`. The `[7,1,3]` weight order circulating in write-ups gives a wrong digit on this example — verify by reproducing the reference, not by memory.

## Postal index and tax-office code

Resolve both from the street, not from intuition: index services list every index for a street, and the same page usually prints the ИФНС code for it. When a house number cannot be confirmed, pick an index valid for that street and say it is unconfirmed.

## Test-data hygiene

- Invented e-mail → reserved domain (`example.ru`), never a plausible `mail.ru` address that may belong to a real person.
- Invented phone → patterned (`+7 (916) 123-45-67`), not a real-looking subscriber number.
- Keep the counterparty's real bank name, БИК and к/с from the template; swap only the subscriber's own account.
- Every invented value goes into the reply as a list, so the user replaces it before signing.
