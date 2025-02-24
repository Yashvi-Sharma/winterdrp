CREATE TABLE IF NOT EXISTS itid( itid INT PRIMARY KEY,  imgtype VARCHAR(20));
INSERT INTO itid (itid, imgtype)
SELECT * FROM (SELECT 1,'SCIENCE' UNION ALL
               SELECT 2,'CAL' UNION ALL
               SELECT 3,'FOCUS' UNION ALL
               SELECT 4,'POINTING' UNION ALL
               SELECT 5,'OTHER') data
               WHERE NOT EXISTS (SELECT NULL FROM itid );
