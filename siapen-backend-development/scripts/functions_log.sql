ALTER TABLE rest_framework_tracking_apirequestlog 
ADD COLUMN response_old text;

create or replace function func_get_response_old(log_id BIGINT)
returns text as 
$$
select response 
from rest_framework_tracking_apirequestlog
where response like func_get_id($1) and id < $1 and view_method <> 'list'
ORDER BY requested_at DESC
LIMIT 1;
$$ language 'sql' STABLE;

create or replace function func_get_id(log_id bigint)
returns text as 
$$
SELECT CONCAT('%',SUBSTRING(response, 8, 36), '%')  
FROM rest_framework_tracking_apirequestlog rfta  
where id = $1;
$$ language 'sql' STABLE;

CREATE OR REPLACE FUNCTION function_update()
RETURNS trigger AS
$BODY$
begin
UPDATE rest_framework_tracking_apirequestlog 
SET response_old = func_get_response_old(new.id)
WHERE id = NEW.id; 
RETURN new;
END;
$BODY$
LANGUAGE plpgsql;

create TRIGGER get_response_old
AFTER insert ON rest_framework_tracking_apirequestlog
FOR EACH ROW
WHEN (NEW.method = 'PUT' or NEW.method = 'PATCH' and NEW.status_code = 200)
EXECUTE function function_update()