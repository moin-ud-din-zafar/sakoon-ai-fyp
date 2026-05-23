-- ============================================
-- Sakoon AI — MySQL Database Setup Script
-- Run: mysql -u root -p < database/init_sakoon.sql
-- Or: Source this file in MySQL Workbench
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS sakoon
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sakoon;

-- ============================================
-- 1. Users Table
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(100) NOT NULL,
    language_preference VARCHAR(10) DEFAULT 'en',
    total_sessions      INT DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_language (language_preference)
);

-- ============================================
-- 2. Sessions Table
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    session_no      INT NOT NULL,
    status          ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    stress_level    INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_sessions_user_session (user_id, session_no),
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_status (status),
    INDEX idx_sessions_created (created_at)
);

-- ============================================
-- 3. Chat Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS chat_logs (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    session_id          INT NOT NULL,
    user_message        TEXT NOT NULL,
    ai_response         TEXT NOT NULL,
    mh_classification   VARCHAR(50),
    mh_confidence       FLOAT,
    emotion_label       VARCHAR(50),
    risk_level          ENUM('low', 'medium', 'high') DEFAULT 'low',
    is_crisis           TINYINT(1) DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_chat_logs_session (session_id),
    INDEX idx_chat_logs_crisis (is_crisis),
    INDEX idx_chat_logs_created (created_at)
);

-- ============================================
-- 4. Emotion History Table
-- ============================================
CREATE TABLE IF NOT EXISTS emotion_history (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    session_id      INT NOT NULL,
    emotion_label   VARCHAR(50) NOT NULL,
    confidence      FLOAT,
    recorded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_emotion_session (session_id),
    INDEX idx_emotion_recorded (recorded_at)
);

-- ============================================
-- 5. Assignments Table (Coping exercises)
-- ============================================
CREATE TABLE IF NOT EXISTS assignments (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    exercise_type   VARCHAR(50) NOT NULL,
    content         TEXT,
    assigned_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed       TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_assignments_user (user_id),
    INDEX idx_assignments_completed (completed)
);

-- ============================================
-- 6. Admin Users Table (optional)
-- ============================================
CREATE TABLE IF NOT EXISTS admin_users (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. Exercise feedback (post “Did this help?”)
-- ============================================
CREATE TABLE IF NOT EXISTS exercise_feedback (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    session_id      INT NULL,
    assignment_id   INT NULL,
    helped          TINYINT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_exercise_feedback_user (user_id)
);

-- ============================================
-- 8. Patient Profiles (Intake Form)
-- ============================================
CREATE TABLE IF NOT EXISTS patient_profiles (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL UNIQUE,
    age             INT,
    gender          VARCHAR(20),
    sleep_pattern   VARCHAR(50),
    stress_triggers TEXT,
    past_therapy    TINYINT(1) DEFAULT 0,
    medications     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_profiles_user (user_id)
);

-- ============================================
-- 9. Assessments (3-session clinical flow)
-- ============================================
CREATE TABLE IF NOT EXISTS assessments (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,   -- 'intake', 'clinical', 'behavioral'
    session_number  INT NOT NULL,           -- 1, 2, or 3
    status          ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_assessments_user (user_id),
    INDEX idx_assessments_status (status)
);

-- ============================================
-- 10. Assessment Answers
-- ============================================
CREATE TABLE IF NOT EXISTS assessment_answers (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    assessment_id   INT NOT NULL,
    question_key    VARCHAR(100) NOT NULL,
    question_text   TEXT NOT NULL,
    answer_value    INT,
    answer_text     TEXT,
    answered_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    INDEX idx_assessment_answers_assessment (assessment_id)
);

-- ============================================
-- 11. Assessment Results (computed scores)
-- ============================================
CREATE TABLE IF NOT EXISTS assessment_results (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    user_id             INT NOT NULL UNIQUE,
    depression_score    INT DEFAULT 0,
    anxiety_score       INT DEFAULT 0,
    risk_level          ENUM('low', 'moderate', 'high', 'critical') DEFAULT 'low',
    depression_severity VARCHAR(30),
    anxiety_severity    VARCHAR(30),
    summary             TEXT,
    recommendations     TEXT,
    completed_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_assessment_results_user (user_id)
);

-- ============================================
-- 12. Daily Mood Logs
-- ============================================
CREATE TABLE IF NOT EXISTS mood_logs (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    mood_score  INT NOT NULL,   -- 1 (very low) to 5 (very good)
    note        TEXT,
    logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_mood_logs_user (user_id),
    INDEX idx_mood_logs_logged (logged_at)
);

-- ============================================
-- 13. Behavior Logs
-- ============================================
CREATE TABLE IF NOT EXISTS behavior_logs (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    user_id             INT NOT NULL,
    sleep_hours         FLOAT,
    physical_activity   VARCHAR(50),   -- 'none', 'light', 'moderate', 'intense'
    social_interaction  VARCHAR(50),   -- 'isolated', 'minimal', 'moderate', 'active'
    notes               TEXT,
    logged_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_behavior_logs_user (user_id),
    INDEX idx_behavior_logs_logged (logged_at)
);

-- ============================================
-- Done! Tables created successfully.
-- ============================================
SELECT 'Sakoon AI database created successfully!' AS message;
