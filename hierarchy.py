# hierarchy.py
# Member Hierarchy - سلسله مراتب اعضای مجموعه

LEVEL_OWNER      = 1
LEVEL_MANAGER    = 2
LEVEL_SUPERVISOR = 3
LEVEL_EMPLOYEE   = 4

ROLE_TO_LEVEL = {
    "owner":      LEVEL_OWNER,
    "both":       LEVEL_OWNER,
    "manager":    LEVEL_MANAGER,
    "supervisor": LEVEL_SUPERVISOR,
    "employee":   LEVEL_EMPLOYEE,
}

LEVEL_TO_ROLE = {
    LEVEL_OWNER:      "owner",
    LEVEL_MANAGER:    "manager",
    LEVEL_SUPERVISOR: "supervisor",
    LEVEL_EMPLOYEE:   "employee",
}

LEVEL_LABELS_FA = {
    LEVEL_OWNER:      "رئیس",
    LEVEL_MANAGER:    "مدیر",
    LEVEL_SUPERVISOR: "سرپرست",
    LEVEL_EMPLOYEE:   "کارمند",
}

def role_to_level(role):
    return ROLE_TO_LEVEL.get(role or "employee", LEVEL_EMPLOYEE)

def get_hierarchy_row(db, complex_id, member_id):
    if not complex_id or not member_id:
        return None
    try:
        return db.fetch_one(
            """
            SELECT hierarchyId, level, supervisorId
            FROM member_hierarchy
            WHERE complexId = %s AND memberId = %s
            LIMIT 1
            """,
            (complex_id, member_id)
        )
    except Exception as e:
        print("HIERARCHY: get_hierarchy_row error:", e)
        return None

def get_member_level(db, complex_id, member_id):
    """سطح کاربر رو از role می‌گیره (نه از جدول hierarchy)"""
    if not complex_id or not member_id:
        return LEVEL_EMPLOYEE
    try:
        row = db.fetch_one(
            """
            SELECT role FROM complex_members
            WHERE complexId = %s AND memberId = %s
            LIMIT 1
            """,
            (complex_id, member_id)
        )
        if row:
            return role_to_level(row.get("role") or "employee")
    except Exception as e:
        print("HIERARCHY: get_member_level error:", e)

    return LEVEL_EMPLOYEE

def get_direct_subordinates(db, complex_id, member_id):
    try:
        rows = db.fetch_all(
            """
            SELECT memberId FROM member_hierarchy
            WHERE complexId = %s AND supervisorId = %s
            """,
            (complex_id, member_id)
        )
        return [r["memberId"] for r in rows]
    except Exception as e:
        print("HIERARCHY: get_direct_subordinates error:", e)
        return []

def get_all_subordinates(db, complex_id, member_id):
    result  = []
    visited = set()
    queue   = [member_id]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        for mid in get_direct_subordinates(db, complex_id, current):
            if mid not in visited:
                result.append(mid)
                queue.append(mid)

    return result

def get_visible_member_ids(db, complex_id, member_id, level=None):
    """
    ═══ محاسبه بر اساس role (نه hierarchy) ═══

    Owner      → همه اعضای فعال
    Manager    → سرپرست‌ها + کارمندها + خودش
    Supervisor → کارمندها + خودش
    Employee   → فقط خودش
    """
    if not complex_id or not member_id:
        return []

    if level is None:
        level = get_member_level(db, complex_id, member_id)

    try:
        # ═══ مالک ═══
        if level == LEVEL_OWNER:
            rows = db.fetch_all(
                """
                SELECT memberId FROM complex_members
                WHERE complexId = %s AND isActive = '1'
                """,
                (complex_id,)
            )
            result = [r["memberId"] for r in rows] if rows else []
            if member_id not in result:
                result.append(member_id)
            return result

        # ═══ کارمند ═══
        if level == LEVEL_EMPLOYEE:
            return [member_id]

        # ═══ مدیر ═══
        if level == LEVEL_MANAGER:
            rows = db.fetch_all(
                """
                SELECT memberId FROM complex_members
                WHERE complexId = %s AND isActive = '1'
                  AND role IN ('supervisor', 'employee')
                """,
                (complex_id,)
            )
            result = [member_id]
            if rows:
                result += [r["memberId"] for r in rows]
            return result

        # ═══ سرپرست ═══
        if level == LEVEL_SUPERVISOR:
            rows = db.fetch_all(
                """
                SELECT memberId FROM complex_members
                WHERE complexId = %s AND isActive = '1'
                  AND role IN ('employee')
                """,
                (complex_id,)
            )
            result = [member_id]
            if rows:
                result += [r["memberId"] for r in rows]
            return result

    except Exception as e:
        print("HIERARCHY: get_visible_member_ids error:", e)

    return [member_id]

def ensure_hierarchy_row(db, complex_id, member_id, role, supervisor_id=None):
    level = role_to_level(role)

    if get_hierarchy_row(db, complex_id, member_id):
        return True

    try:
        db.execute(
            """
            INSERT INTO member_hierarchy
            (complexId, memberId, supervisorId, level, createdDate)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (complex_id, member_id, supervisor_id, level)
        )
        return True
    except Exception as e:
        print("HIERARCHY: ensure_hierarchy_row error:", e)
        return False

def set_supervisor_and_level(db, complex_id, member_id, supervisor_id, level):
    try:
        existing = get_hierarchy_row(db, complex_id, member_id)
        if existing:
            db.execute(
                """
                UPDATE member_hierarchy
                SET supervisorId = %s, level = %s, updatedDate = NOW()
                WHERE hierarchyId = %s
                """,
                (supervisor_id, level, existing["hierarchyId"])
            )
        else:
            db.execute(
                """
                INSERT INTO member_hierarchy
                (complexId, memberId, supervisorId, level, createdDate)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (complex_id, member_id, supervisor_id, level)
            )
        return True
    except Exception as e:
        print("HIERARCHY: set_supervisor_and_level error:", e)
        return False

def get_potential_supervisors(db, complex_id, exclude_member_id=None):
    try:
        query = """
            SELECT cm.memberId, cm.role, u.name,
                   COALESCE(mh.level, 4) AS level
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN member_hierarchy mh
                ON mh.memberId = cm.memberId
               AND mh.complexId = cm.complexId
            WHERE cm.complexId = %s
              AND cm.isActive = '1'
              AND cm.role IN ('owner', 'both', 'manager', 'supervisor')
        """
        params = [complex_id]

        if exclude_member_id:
            query += " AND cm.memberId != %s"
            params.append(exclude_member_id)

        query += " ORDER BY level ASC, u.name ASC"

        rows = db.fetch_all(query, tuple(params))
        return rows or []
    except Exception as e:
        print("HIERARCHY: get_potential_supervisors error:", e)
        return []

def get_supervisors_for_role(db, complex_id, role):
    try:
        if role == "employee":
            allowed_roles = ("supervisor", "manager", "owner", "both")
        elif role == "supervisor":
            allowed_roles = ("manager", "owner", "both")
        elif role == "manager":
            allowed_roles = ("owner", "both")
        else:
            return []

        placeholders = ",".join(["%s"] * len(allowed_roles))

        rows = db.fetch_all(
            f"""
            SELECT cm.memberId, cm.role, u.name,
                   COALESCE(mh.level, 4) AS level
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN member_hierarchy mh
                ON mh.memberId = cm.memberId
               AND mh.complexId = cm.complexId
            WHERE cm.complexId = %s
              AND cm.isActive = '1'
              AND cm.role IN ({placeholders})
            ORDER BY level ASC, u.name ASC
            """,
            (complex_id, *allowed_roles)
        )
        return rows or []
    except Exception as e:
        print("HIERARCHY: get_supervisors_for_role error:", e)
        return []