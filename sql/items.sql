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
    `name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
    `email` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `phone` int(10) NOT NULL,
    `address` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
    `city` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `payment` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
    `time` timestamp NOT NULL,
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `upload`;
CREATE TABLE `upload` (
    `itemid` int(10) NOT NULL,
    `filename` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
KEY `itemid_idx` (`itemid`),
CONSTRAINT `fk_itemidid` FOREIGN KEY (`itemid`) REFERENCES `items` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;