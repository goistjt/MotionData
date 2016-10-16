CREATE PROCEDURE `delete_entire_session` (IN session_id int(32))
BEGIN
	DELETE FROM Session WHERE Session.id = session_id;
    DECLARE max_id SELECT MAX( `id` ) FROM Session;
    ALTER TABLE Session AUTO_INCREMENT = max_id+1;
    
    SELECT id FROM Records WHERE session_id = session_id;

    #For each record

    DELETE FROM AccessPoints
    WHERE AccessPoints.record_id = record_id
    DELETE FROM GyroPoints
    WHERE GyroPoints.record_id = record_id
    #END of the for loop

    DELETE FROM Records WHERE Records.session_id = session_id

END
