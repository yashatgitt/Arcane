import sqlite3
import os

# Ensures we target the DB in the same directory as the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'arcane.db')

def flush_db():
    print("\n" + "!" * 40)
    print("!!  A.R.C.A.N.E. DATABASE FLUSH TOOL !!")
    print("!" * 40)
    print(f"\nTarget: {DB_PATH}")
    print("This will PERMANENTLY delete:")
    print(" - All User Accounts in SQLite")
    print(" - All Message Histories in SQLite")
    print("\nLogs (user_list.txt, etc.) will NOT be touched.")
    
    confirm = input("\nTo proceed, type 'FLUSH' (all caps): ").strip()
    
    if confirm != 'FLUSH':
        print("\n[!] Flush aborted. No changes made.")
        return

    if not os.path.exists(DB_PATH):
        print(f"\n[ERROR] Database not found at {DB_PATH}")
        return

    try:
        print("\n[+] Opening connection...")
        conn = sqlite3.connect(DB_PATH)
        db = conn.cursor()
        
        # 1. Wipe Data
        print("[~] Wiping SQLite tables...")
        db.execute('DELETE FROM messages;')
        db.execute('DELETE FROM users;')
        
        # 2. Reset Sequence
        print("[~] Resetting auto-increment counters...")
        db.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'messages');")
        
        # 3. VACUUM (Force physical cleanup and WAL sync)
        print("[~] Performing VACUUM cleanup...")
        conn.commit()
        db.execute("VACUUM;")
        
        # 4. Final verification
        db.execute("SELECT count(*) FROM users;")
        u_count = db.fetchone()[0]
        db.execute("SELECT count(*) FROM messages;")
        m_count = db.fetchone()[0]
        
        conn.close()
        print(f"\n[OK] Database flushed successfully.")
        print(f"[Verification] Users remaining: {u_count} | Messages remaining: {m_count}")
        
    except Exception as e:
        print(f"\n[ERROR] Flush failed: {e}")

    print("\n" + "=" * 40)
    print("!!      FLUSH SEQUENCE COMPLETE      !!")
    print("=" * 40)

if __name__ == "__main__":
    flush_db()
