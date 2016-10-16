USE `six-dof`;
SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw,
            AccessPoints.surge, AccessPoints.sway, AccessPoints.heave
            FROM GyroPoints INNER JOIN AccessPoints
            ON GyroPoints.record_id = '2c2b3609c6a7eefb232d816dd0222f42ee3eaa5b'
            AND GyroPoints.timestamp = AccessPoints.timestamp
            ORDER BY GyroPoints.timestamp ASC