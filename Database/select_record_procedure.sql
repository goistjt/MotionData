CREATE  PROCEDURE `select_record`(
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
END