-- ═══════════════════════════════════════════════════════════
-- Member Hierarchy (سلسله مراتب اعضای مجموعه)
-- Created: 2026-10-09
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `member_hierarchy` (
  `hierarchyId` int(11) NOT NULL AUTO_INCREMENT,
  `complexId` int(11) NOT NULL,
  `memberId` int(11) NOT NULL,
  `supervisorId` int(11) DEFAULT NULL,
  `level` int(11) NOT NULL DEFAULT 4,
  `createdDate` datetime NOT NULL,
  `updatedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`hierarchyId`),
  UNIQUE KEY `uq_hier_member` (`complexId`, `memberId`),
  KEY `idx_hier_supervisor` (`complexId`, `supervisorId`),
  KEY `idx_hier_level` (`complexId`, `level`),
  CONSTRAINT `fk_hier_complex`
    FOREIGN KEY (`complexId`)
    REFERENCES `complexes` (`complexId`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_hier_member`
    FOREIGN KEY (`memberId`)
    REFERENCES `complex_members` (`memberId`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_hier_supervisor`
    FOREIGN KEY (`supervisorId`)
    REFERENCES `complex_members` (`memberId`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- ═══════════════════════════════════════════════════════════
-- مقدار اولیه برای اعضای موجود
-- ═══════════════════════════════════════════════════════════

-- ۱) مالک‌های مجموعه‌ها → level 1، بدون رئیس
INSERT IGNORE INTO `member_hierarchy`
  (`complexId`, `memberId`, `supervisorId`, `level`, `createdDate`)
SELECT
  cm.`complexId`,
  cm.`memberId`,
  NULL,
  1,
  NOW()
FROM `complex_members` cm
WHERE cm.`role` IN ('owner', 'both')
  AND cm.`isActive` = '1';

-- ۲) کارمندها → level 4، بدون رئیس (بعداً مالک تعیین می‌کنه)
INSERT IGNORE INTO `member_hierarchy`
  (`complexId`, `memberId`, `supervisorId`, `level`, `createdDate`)
SELECT
  cm.`complexId`,
  cm.`memberId`,
  NULL,
  4,
  NOW()
FROM `complex_members` cm
WHERE cm.`role` = 'employee'
  AND cm.`isActive` = '1';