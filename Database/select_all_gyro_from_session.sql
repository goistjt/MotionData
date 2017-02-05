USE `six-dof`;
DROP procedure IF EXISTS `select_all_gyro_from_session`;
CREATE PROCEDURE `select_all_gyro_from_session`(
	sid int(30)
)
BEGIN
select record_id, roll, pitch, yaw, `timestamp` from 
(select r.id as session_record_id from Records as r where r.session_id = sid) as current_session
left join
GyroPoints
on session_record_id = GyroPoints.record_id
order by `timestamp`;
END