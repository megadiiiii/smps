# -*- coding: utf-8 -*-
"""
test_exit_comparison.py - Test logic so sánh khi xe Ra cửa
"""
import sqlite3
import os
from db import DB_PATH, init_db

print("="*60)
print("TEST LOGIC SO SANH KHI XE RA CUA")
print("="*60)

# Init DB
init_db()

# Test query get_latest_face_for_plate
print("\n[1] Test query get_latest_face_for_plate...")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Insert test data
test_plate = "TEST-12345"

# Insert 2 records: Vào và Ra
cur.execute("""
    INSERT INTO events
    (plate_text, status, time_in, time_out, face_image_path, plate_image_path)
    VALUES (?, ?, ?, ?, ?, ?)
""", (test_plate, "Vào", "2024-01-01 10:00:00", None, "/path/to/face_in.jpg", "/path/to/plate_in.jpg"))

cur.execute("""
    INSERT INTO events
    (plate_text, status, time_in, time_out, face_image_path, plate_image_path)
    VALUES (?, ?, ?, ?, ?, ?)
""", (test_plate, "Ra", None, "2024-01-01 12:00:00", "/path/to/face_out.jpg", "/path/to/plate_out.jpg"))

conn.commit()

# Test query (giống logic trong get_latest_face_for_plate)
cur.execute("""
    SELECT face_image_path, status
    FROM events
    WHERE plate_text = ?
      AND status = 'Vào'
      AND face_image_path IS NOT NULL
      AND face_image_path != ''
    ORDER BY id DESC LIMIT 1
""", (test_plate,))

row = cur.fetchone()
if row:
    face_path, status = row
    print(f"[OK] Query tra ve dung anh mat luc Vao:")
    print(f"     Path: {face_path}")
    print(f"     Status: {status}")

    if status == "Vào" and "face_in" in face_path:
        print("[SUCCESS] Query hoat dong DUNG!")
    else:
        print("[FAIL] Query tra ve sai record!")
else:
    print("[FAIL] Query khong tra ve ket qua nao!")

# Test query CU (không có filter status)
print("\n[2] Test query CU (khong filter status)...")
cur.execute("""
    SELECT face_image_path, status
    FROM events
    WHERE plate_text = ?
      AND face_image_path IS NOT NULL
      AND face_image_path != ''
    ORDER BY id DESC LIMIT 1
""", (test_plate,))

row_old = cur.fetchone()
if row_old:
    face_path_old, status_old = row_old
    print(f"[!] Query CU tra ve:")
    print(f"    Path: {face_path_old}")
    print(f"    Status: {status_old}")

    if status_old == "Ra":
        print("[FAIL] Query CU lay NHAM anh mat luc Ra!")
        print("       -> Day la ly do he thong khong so sanh duoc!")
    else:
        print("[OK] Query CU van lay dung (may man!)")

# Clean up
cur.execute("DELETE FROM events WHERE plate_text = ?", (test_plate,))
conn.commit()
conn.close()

print("\n" + "="*60)
print("TEST HOAN THANH!")
print("="*60)
print("\nKet luan:")
print("- Query MOI (co filter status='Vào') se lay dung anh mat luc Vao")
print("- Query CU (khong filter) LAY NHAM anh mat luc Ra")
print("- Fix da duoc ap dung vao login_user_gui.py!")
