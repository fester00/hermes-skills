#!/usr/bin/env python3
"""
Pre-flight check for subagent batches.
Usage: python3 scripts/check-auth-pool.py [provider]

Exits 0 if all keys OK, 1 if any exhausted.
Prints status of all credentials in the pool.
"""
import json, os, sys

PROVIDER = sys.argv[1] if len(sys.argv) > 1 else 'ollama-cloud'
AUTH_FILE = os.path.expanduser('~/.hermes/auth.json')

def main():
    if not os.path.exists(AUTH_FILE):
        print(f"WARN: {AUTH_FILE} not found")
        sys.exit(0)
    
    data = json.load(open(AUTH_FILE))
    pool = data.get('credential_pool', {})
    
    if PROVIDER not in pool:
        print(f"INFO: No credentials for provider '{PROVIDER}'")
        sys.exit(0)
    
    entries = pool[PROVIDER]
    exhausted = []
    ok = []
    
    for i, e in enumerate(entries):
        status = e.get('last_status', 'ok')
        if status == 'exhausted':
            exhausted.append((i, e.get('last_error_code', 'unknown')))
        else:
            ok.append(i)
    
    print(f"Provider: {PROVIDER}")
    print(f"  Total keys: {len(entries)}")
    print(f"  OK: {len(ok)}")
    print(f"  Exhausted: {len(exhausted)}")
    
    if exhausted:
        for idx, code in exhausted:
            print(f"    [{idx}] EXHAUSTED (last error: {code})")
        print(f"\nFIX: hermes auth reset {PROVIDER}")
        sys.exit(1)
    else:
        print("  All keys ready. Safe to dispatch subagents.")
        sys.exit(0)

if __name__ == '__main__':
    main()
