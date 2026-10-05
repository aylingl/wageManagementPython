-- ═══════════════════════════════════════════════════════════
-- Initial Schema for Wage Management System
-- Created: 2026-10-05
-- ═══════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════
-- 1) users
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `users` (
  `userId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_persian_ci NOT NULL,
  `profession` varchar(100) COLLATE utf8mb4_persian_ci NOT NULL DEFAULT 'unknown',
  `nationalId` char(10) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  `passwordHash` varchar(255) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  `countryCode` varchar(6) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  `phoneNumber` varchar(11) COLLATE utf8mb4_persian_ci NOT NULL,
  `createdDate` datetime NOT NULL,
  `sentOtp` int(11) DEFAULT '0',
  `otpSentDateTime` datetime DEFAULT NULL,
  `otpUsed` enum('0','1') COLLATE utf8mb4_persian_ci NOT NULL DEFAULT '0',
  `imageBase64` longtext COLLATE utf8mb4_persian_ci,
  `birthDate` varchar(10) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  `isActive` enum('0','1') COLLATE utf8mb4_persian_ci NOT NULL DEFAULT '1',
  `imageHash` varchar(64) COLLATE utf8mb4_persian_ci DEFAULT NULL,
  PRIMARY KEY (`userId`),
  UNIQUE KEY `uq_users_nationalId` (`nationalId`),
  UNIQUE KEY `uq_users_phone` (`countryCode`,`phoneNumber`),
  UNIQUE KEY `uq_users_email` (`email`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- ═══════════════════════════════════════════════════════════
-- 2) complexes
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `complexes` (
  `complexId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` text,
  `description` text,
  `activity` varchar(255) NOT NULL,
  `ownerId` int(11) NOT NULL,
  `createdDate` datetime NOT NULL,
  `isActive` enum('0','1') NOT NULL DEFAULT '1',
  PRIMARY KEY (`complexId`),
  KEY `fk_complexes_owner` (`ownerId`),
  CONSTRAINT `fk_complexes_owner` FOREIGN KEY (`ownerId`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 3) complex_members
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `complex_members` (
  `memberId` int(11) NOT NULL AUTO_INCREMENT,
  `complexId` int(11) NOT NULL,
  `userId` int(11) NOT NULL,
  `role` enum('owner','employee','both') NOT NULL,
  `joinedDate` datetime NOT NULL,
  `isActive` enum('0','1') NOT NULL DEFAULT '1',
  PRIMARY KEY (`memberId`),
  UNIQUE KEY `uq_complex_member` (`complexId`,`userId`),
  KEY `fk_members_user` (`userId`),
  CONSTRAINT `fk_members_complex` FOREIGN KEY (`complexId`) REFERENCES `complexes` (`complexId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_members_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 4) employee_profiles
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `employee_profiles` (
  `employeeProfileId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `jobTitle` varchar(255) NOT NULL,
  `nationalCode` varchar(10) DEFAULT NULL,
  `employmentType` enum('fullTime','partTime','daily','monthly','hourly','percentage','count','weight','length') NOT NULL,
  `salaryType` enum('monthly','daily','hourly') NOT NULL DEFAULT 'monthly',
  `baseSalary` decimal(15,2) NOT NULL DEFAULT '0.00',
  `workDays` decimal(5,2) NOT NULL DEFAULT '26.00',
  `workHours` decimal(5,2) NOT NULL DEFAULT '8.00',
  `workStartTime` time DEFAULT NULL,
  `workEndTime` time DEFAULT NULL,
  `description` text,
  `canSeeEmployees` enum('0','1') NOT NULL DEFAULT '1',
  `createdDate` datetime NOT NULL,
  `allowOvertime` enum('0','1') NOT NULL DEFAULT '1',
  PRIMARY KEY (`employeeProfileId`),
  UNIQUE KEY `uq_employee_profile_member` (`memberId`),
  CONSTRAINT `fk_employee_profiles_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 5) jobs
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `jobs` (
  `jobId` int(11) NOT NULL AUTO_INCREMENT,
  `complexId` int(11) NOT NULL,
  `jobTitle` varchar(255) NOT NULL,
  `description` text,
  `employmentType` enum('fullTime','partTime','daily','monthly','hourly','percentage','count','weight','length') NOT NULL,
  `basePrice` decimal(15,2) NOT NULL DEFAULT '0.00',
  `isActive` enum('0','1') NOT NULL DEFAULT '1',
  `createdDate` datetime NOT NULL,
  PRIMARY KEY (`jobId`),
  KEY `fk_jobs_complex` (`complexId`),
  CONSTRAINT `fk_jobs_complex` FOREIGN KEY (`complexId`) REFERENCES `complexes` (`complexId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 6) employee_jobs
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `employee_jobs` (
  `employeeJobId` int(11) NOT NULL AUTO_INCREMENT,
  `jobId` int(11) NOT NULL,
  `memberId` int(11) NOT NULL,
  `assignedBy` int(11) NOT NULL,
  `assignedDate` datetime NOT NULL,
  `startDate` date DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `quantity` decimal(15,2) DEFAULT NULL,
  `price` decimal(15,2) NOT NULL DEFAULT '0.00',
  `status` enum('pending','inProgress','completed','rejected','cancelled') NOT NULL DEFAULT 'pending',
  `description` text,
  `completedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`employeeJobId`),
  KEY `fk_employee_jobs_job` (`jobId`),
  KEY `fk_employee_jobs_member` (`memberId`),
  KEY `fk_employee_jobs_assignedBy` (`assignedBy`),
  CONSTRAINT `fk_employee_jobs_assignedBy` FOREIGN KEY (`assignedBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_employee_jobs_job` FOREIGN KEY (`jobId`) REFERENCES `jobs` (`jobId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_employee_jobs_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 7) job_approvals
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `job_approvals` (
  `approvalId` int(11) NOT NULL AUTO_INCREMENT,
  `employeeJobId` int(11) NOT NULL,
  `approvedBy` int(11) NOT NULL,
  `status` enum('approved','rejected') NOT NULL,
  `approvalDate` datetime NOT NULL,
  `description` text,
  PRIMARY KEY (`approvalId`),
  KEY `fk_job_approvals_job` (`employeeJobId`),
  KEY `fk_job_approvals_user` (`approvedBy`),
  CONSTRAINT `fk_job_approvals_job` FOREIGN KEY (`employeeJobId`) REFERENCES `employee_jobs` (`employeeJobId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_job_approvals_user` FOREIGN KEY (`approvedBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 8) attendance
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `attendance` (
  `attendanceId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `workDate` date NOT NULL,
  `checkIn` datetime DEFAULT NULL,
  `checkOut` datetime DEFAULT NULL,
  `workedMinutes` int(11) NOT NULL DEFAULT '0',
  `overtimeMinutes` int(11) NOT NULL DEFAULT '0',
  `status` enum('present','absent','late','leave') NOT NULL DEFAULT 'present',
  `approvalStatus` enum('pending','approved','rejected') DEFAULT 'pending',
  `approvedBy` int(11) DEFAULT NULL,
  `approvalDate` datetime DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`attendanceId`),
  UNIQUE KEY `uq_attendance_member_date` (`memberId`,`workDate`),
  CONSTRAINT `fk_attendance_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 9) leaves
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `leaves` (
  `leaveId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `leaveType` enum('daily','hourly','sick','unpaid','other') NOT NULL,
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `reason` text,
  `approvedBy` int(11) DEFAULT NULL,
  `createdDate` datetime NOT NULL,
  PRIMARY KEY (`leaveId`),
  KEY `fk_leaves_member` (`memberId`),
  KEY `fk_leaves_approvedBy` (`approvedBy`),
  CONSTRAINT `fk_leaves_approvedBy` FOREIGN KEY (`approvedBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_leaves_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 10) loans
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `loans` (
  `loanId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `totalAmount` decimal(15,2) NOT NULL,
  `installmentAmount` decimal(15,2) NOT NULL,
  `installmentCount` int(11) NOT NULL,
  `remainingAmount` decimal(15,2) NOT NULL,
  `startDate` date NOT NULL,
  `status` enum('active','completed','cancelled') NOT NULL DEFAULT 'active',
  `description` text,
  `createdDate` datetime NOT NULL,
  PRIMARY KEY (`loanId`),
  KEY `fk_loans_member` (`memberId`),
  CONSTRAINT `fk_loans_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 11) loan_installments
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `loan_installments` (
  `installmentId` int(11) NOT NULL AUTO_INCREMENT,
  `loanId` int(11) NOT NULL,
  `installmentNumber` int(11) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `dueDate` date NOT NULL,
  `paidDate` date DEFAULT NULL,
  `status` enum('pending','paid','late') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`installmentId`),
  UNIQUE KEY `uq_loan_installment` (`loanId`,`installmentNumber`),
  CONSTRAINT `fk_installments_loan` FOREIGN KEY (`loanId`) REFERENCES `loans` (`loanId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 12) salaries
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `salaries` (
  `salaryId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `salaryYear` int(11) NOT NULL,
  `salaryMonth` int(11) NOT NULL,
  `baseSalary` decimal(15,2) NOT NULL DEFAULT '0.00',
  `overtimeAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `bonusAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `benefitAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `insuranceAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `taxAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `deductionAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `loanAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `advanceAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `finalAmount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `status` enum('draft','calculated','paid') NOT NULL DEFAULT 'draft',
  `createdDate` datetime NOT NULL,
  `paidDate` datetime DEFAULT NULL,
  `paidBy` int(11) DEFAULT NULL,
  PRIMARY KEY (`salaryId`),
  UNIQUE KEY `uq_salary_member_month` (`memberId`,`salaryYear`,`salaryMonth`),
  KEY `fk_salaries_paidBy` (`paidBy`),
  CONSTRAINT `fk_salaries_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_salaries_paidBy` FOREIGN KEY (`paidBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 13) bonuses
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `bonuses` (
  `bonusId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `bonusDate` date NOT NULL,
  `createdBy` int(11) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'approved',
  `approvedBy` int(11) DEFAULT NULL,
  PRIMARY KEY (`bonusId`),
  KEY `fk_bonuses_member` (`memberId`),
  KEY `fk_bonuses_creator` (`createdBy`),
  KEY `fk_bonuses_approvedBy` (`approvedBy`),
  CONSTRAINT `fk_bonuses_approvedBy` FOREIGN KEY (`approvedBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bonuses_creator` FOREIGN KEY (`createdBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bonuses_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 14) deductions
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `deductions` (
  `deductionId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `deductionDate` date NOT NULL,
  `createdBy` int(11) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'approved',
  `approvedBy` int(11) DEFAULT NULL,
  `deductionType` varchar(20) NOT NULL DEFAULT 'normal',
  `intentPurpose` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`deductionId`),
  KEY `fk_deductions_member` (`memberId`),
  KEY `fk_deductions_creator` (`createdBy`),
  KEY `fk_deductions_approvedBy` (`approvedBy`),
  CONSTRAINT `fk_deductions_approvedBy` FOREIGN KEY (`approvedBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_deductions_creator` FOREIGN KEY (`createdBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_deductions_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 15) payments
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `payments` (
  `paymentId` int(11) NOT NULL AUTO_INCREMENT,
  `memberId` int(11) NOT NULL,
  `complexId` int(11) DEFAULT NULL,
  `employeeJobId` int(11) DEFAULT NULL,
  `salaryId` int(11) DEFAULT NULL,
  `amount` decimal(15,2) NOT NULL,
  `paymentType` enum('salary','job','bonus','advance','other') NOT NULL,
  `paymentDate` datetime NOT NULL,
  `paidBy` int(11) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`paymentId`),
  KEY `fk_payments_member` (`memberId`),
  KEY `fk_payments_employee_job` (`employeeJobId`),
  KEY `fk_payments_salary` (`salaryId`),
  KEY `fk_payments_complex` (`complexId`),
  KEY `fk_payments_paidBy` (`paidBy`),
  CONSTRAINT `fk_payments_complex` FOREIGN KEY (`complexId`) REFERENCES `complexes` (`complexId`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_employee_job` FOREIGN KEY (`employeeJobId`) REFERENCES `employee_jobs` (`employeeJobId`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_member` FOREIGN KEY (`memberId`) REFERENCES `complex_members` (`memberId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_paidBy` FOREIGN KEY (`paidBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_salary` FOREIGN KEY (`salaryId`) REFERENCES `salaries` (`salaryId`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 16) events
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `events` (
  `eventId` int(11) NOT NULL AUTO_INCREMENT,
  `complexId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `eventDate` datetime NOT NULL,
  `createdDate` datetime NOT NULL,
  PRIMARY KEY (`eventId`),
  KEY `fk_events_complex` (`complexId`),
  KEY `fk_events_creator` (`createdBy`),
  CONSTRAINT `fk_events_complex` FOREIGN KEY (`complexId`) REFERENCES `complexes` (`complexId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_events_creator` FOREIGN KEY (`createdBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 17) messages
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `senderId` int(11) NOT NULL,
  `receiverId` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `sentDate` datetime NOT NULL,
  `isRead` enum('0','1') NOT NULL DEFAULT '0',
  PRIMARY KEY (`messageId`),
  KEY `fk_messages_sender` (`senderId`),
  KEY `fk_messages_receiver` (`receiverId`),
  CONSTRAINT `fk_messages_receiver` FOREIGN KEY (`receiverId`) REFERENCES `users` (`userId`) ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_sender` FOREIGN KEY (`senderId`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 18) reports
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `reports` (
  `reportId` int(11) NOT NULL AUTO_INCREMENT,
  `complexId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `reportType` enum('attendance','finance','employees','jobs','salary','general') NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `createdDate` datetime NOT NULL,
  PRIMARY KEY (`reportId`),
  KEY `fk_reports_complex` (`complexId`),
  KEY `fk_reports_creator` (`createdBy`),
  CONSTRAINT `fk_reports_complex` FOREIGN KEY (`complexId`) REFERENCES `complexes` (`complexId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reports_creator` FOREIGN KEY (`createdBy`) REFERENCES `users` (`userId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 19) user_settings
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `user_settings` (
  `settingId` int(11) NOT NULL AUTO_INCREMENT,
  `userId` int(11) NOT NULL,
  `notificationsEnabled` enum('0','1') NOT NULL DEFAULT '1',
  `messageNotifications` enum('0','1') NOT NULL DEFAULT '1',
  `attendanceNotifications` enum('0','1') NOT NULL DEFAULT '1',
  `financeNotifications` enum('0','1') NOT NULL DEFAULT '1',
  `themeName` varchar(20) NOT NULL DEFAULT 'light',
  `language` varchar(10) NOT NULL DEFAULT 'fa',
  PRIMARY KEY (`settingId`),
  UNIQUE KEY `uq_user_settings_user` (`userId`),
  CONSTRAINT `fk_user_settings_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 20) pending_otps
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `pending_otps` (
  `otpId` int(11) NOT NULL AUTO_INCREMENT,
  `countryCode` varchar(6) NOT NULL,
  `phoneNumber` varchar(11) NOT NULL,
  `otpCode` int(11) NOT NULL,
  `createdDate` datetime NOT NULL,
  `expiresDate` datetime NOT NULL,
  `used` enum('0','1') NOT NULL DEFAULT '0',
  PRIMARY KEY (`otpId`),
  KEY `idx_pending_otp_phone` (`countryCode`,`phoneNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- 21) otp_history
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS `otp_history` (
  `otpId` int(11) NOT NULL AUTO_INCREMENT,
  `userId` int(11) NOT NULL,
  `otpCode` int(11) NOT NULL,
  `sentDateTime` datetime NOT NULL,
  `used` enum('0','1') NOT NULL DEFAULT '0',
  PRIMARY KEY (`otpId`),
  KEY `fk_otp_history_user` (`userId`),
  CONSTRAINT `fk_otp_history_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ═══════════════════════════════════════════════════════════
-- Schema migrations tracking table
-- ═══════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════
-- End of initial schema
-- ═══════════════════════════════════════════════════════════