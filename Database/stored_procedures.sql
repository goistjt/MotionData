DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `add_session`(
input_d varchar(255),
input_st double
)
BEGIN
START TRANSACTION;
INSERT INTO Session (description, starting_time) VALUES( input_d, input_st );
COMMIT;
SELECT LAST_INSERT_ID();
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_record`(
	id_in varchar(255),
    session_id int,
    device_id varchar(255)
)
BEGIN
START TRANSACTION;
INSERT INTO Records (id, session_id, device_id) VALUES(id_in, session_id, device_id);
COMMIT;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `delete_session`(
	session_id INT
)
BEGIN
	START TRANSACTION;
    DELETE FROM `Session` WHERE id = session_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_all_records_from_session`(
s_id int(32)
)
BEGIN
SELECT Records.id, Records.session_id, Records.device_id FROM Records where session_id = s_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_sessions_related_to_device`(
device varchar(255)
)
BEGIN
SELECT * FROM Session WHERE id in (SELECT session_id FROM Records WHERE device_id = device);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_session_id`(
description_in varchar(255),
starting_time_in double
)
BEGIN
SELECT * FROM Session WHERE description = description_in AND starting_time = starting_time_in;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `reset_session_auto_index`()
BEGIN
	DECLARE final_index INT;
	DECLARE count INT;
    SELECT count(`id`) INTO @count FROM `Session`;
	IF count <> 0 THEN
		SET final_index = (SELECT MAX( `id` ) FROM `Session`)+1;
	ELSE
		SET final_index = 1;
	END IF;
    SET @SQL := CONCAT('ALTER TABLE Session AUTO_INCREMENT =  ', final_index);
	PREPARE _stmt FROM @SQL;
    START TRANSACTION;
    EXECUTE _stmt;
	COMMIT;
    DEALLOCATE PREPARE _stmt;
   
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `select_accel`(
	record_id_in varchar(255)
)
BEGIN
	SELECT AccelPoints.timestamp, AccelPoints.surge, AccelPoints.sway, AccelPoints.heave
    FROM AccelPoints WHERE AccelPoints.record_id = record_id_in ORDER BY AccelPoints.timestamp ASC;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `select_all_accel_from_session`(
	sid int(30)
)
BEGIN
select `timestamp`, surge, sway, heave from 
(select r.id as session_record_id from Records as r where r.session_id = sid) as current_session
left join
AccelPoints
on session_record_id = AccelPoints.record_id
order by `timestamp`;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `select_all_gyro_from_session`(
	sid int(30)
)
BEGIN
select `timestamp`, roll, pitch, yaw from 
(select r.id as session_record_id from Records as r where r.session_id = sid) as current_session
left join
GyroPoints
on session_record_id = GyroPoints.record_id
order by `timestamp`;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `select_gyro`(
record_id_in varchar(255)
)
BEGIN
	SELECT GyroPoints.timestamp, GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw
	FROM GyroPoints WHERE GyroPoints.record_id = record_id_in ORDER BY GyroPoints.timestamp ASC;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `select_record`(
record varchar(255)
)
BEGIN
SELECT  AccelPoints.timestamp,  AccelPoints.surge, AccelPoints.sway, AccelPoints.heave, GyroPoints.roll,  GyroPoints.pitch, GyroPoints.yaw FROM AccelPoints 
LEFT OUTER JOIN GyroPoints 
ON AccelPoints.timestamp = GyroPoints.timestamp 
WHERE AccelPoints.record_id = record AND (GyroPoints.record_id = record or GyroPoints.record_id is null) 

UNION ALL

SELECT  GyroPoints.timestamp, AccelPoints.surge, AccelPoints.sway, AccelPoints.heave, GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw FROM AccelPoints 
RIGHT OUTER JOIN GyroPoints 
ON AccelPoints.timestamp = GyroPoints.timestamp 
WHERE GyroPoints.record_id = record AND (AccelPoints.record_id = record or AccelPoints.record_id is null) 
ORDER BY timestamp ASC;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_device_entry`(
	device_id_in varchar(255),
    device_name_in varchar(255)
)
BEGIN
START TRANSACTION;
INSERT INTO DeviceNames (device_name, device_id) VALUES(device_name_in, device_id_in);
COMMIT;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_device_entry`(
	device_id_in varchar(255),
    device_name_in varchar(255)
)
BEGIN
START TRANSACTION;
UPDATE DeviceNames SET device_name = device_name_in WHERE device_id = device_id_in;
COMMIT;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_device_name`(
	device_id_in varchar(255)
)
BEGIN
START TRANSACTION;
SELECT device_name FROM DeviceNames WHERE device_id = device_id_in LIMIT 1;
COMMIT;
END$$
DELIMITER ;



