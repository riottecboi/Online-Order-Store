ALTER TABLE orders
ADD COLUMN ordercode tinytext AFTER identified;
ALTER TABLE orders
ADD COLUMN note MEDIUMTEXT AFTER timeship;