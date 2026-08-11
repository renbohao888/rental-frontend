-- =====================================================
-- 站内消息表（系统消息 + 房源分享消息）
-- =====================================================
CREATE TABLE IF NOT EXISTS `message` (
    `id`            BIGINT       NOT NULL COMMENT '主键ID',
    `type`          VARCHAR(32)  DEFAULT NULL COMMENT '消息类型: share-分享房源, repair-报修反馈, dispute-纠纷消息, landlord-房东消息',
    `content`       TEXT         DEFAULT NULL COMMENT '消息内容',
    `sender_id`     BIGINT       DEFAULT NULL COMMENT '发送者用户ID',
    `user_id`       BIGINT       DEFAULT NULL COMMENT '接收者用户ID（消息所属人）',
    `relation_id`   BIGINT       DEFAULT NULL COMMENT '关联业务ID：房源ID/报修ID/纠纷ID',
    `is_read`       INT          DEFAULT 0  COMMENT '是否已读：0-未读 1-已读',
    `create_time`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`    INT          DEFAULT 0  COMMENT '逻辑删除：0-正常 1-已删除',
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_is_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站内消息表';