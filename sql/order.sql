ALTER TABLE orders
ADD COLUMN ordercode tinytext AFTER identified;
ALTER TABLE orders
ADD COLUMN note MEDIUMTEXT AFTER timeship;
ALTER TABLE orders
ADD COLUMN checked tinyint(1) default 0 AFTER note;