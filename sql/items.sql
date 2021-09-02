DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `displayname` varchar (32) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(128) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(128) COLLATE utf8_unicode_ci,
  `telephone` varchar(12) COLLATE utf8_unicode_ci,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  UNIQUE KEY `classify_idx` (`username`),
  PRIMARY KEY (`id`),
  KEY `username_idx` (`username`),
  KEY `apikey_idx` (`apikey`) USING BTREE,
  KEY `enable_idx` (`enable`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `items`;
CREATE TABLE `items` (
    `id` int(10) NOT NULL AUTO_INCREMENT,
    `title` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
    `description` MEDIUMTEXT NOT NULL,
    `price` int(10) NOT NULL,
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
    `id` int(10) NOT NULL AUTO_INCREMENT,
    `identified` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
    `name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
    `email` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `phone` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
    `address` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
    `city` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `payment` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `total` int(10) NOT NULL,
    `time` timestamp NOT NULL default CURRENT_TIMESTAMP,
    `dayship` varchar(32),
    `timeship` varchar(8),
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
    `id` int(10) NOT NULL AUTO_INCREMENT,
    `name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
    `phone` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
    `subject` varchar(200) COLLATE utf8_unicode_ci ,
    `message` MEDIUMTEXT NOT NULL,
    `time` timestamp NOT NULL default CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `name_idx` (`name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
    `itemid` int(10) NOT NULL AUTO_INCREMENT,
    `quantity` int(4) NOT NULL,
    `price` int(10) NOT NULL,
    `identified` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
KEY `itemid_idx` (`itemid`),
CONSTRAINT `fk_itemid` FOREIGN KEY (`itemid`) REFERENCES `items` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
