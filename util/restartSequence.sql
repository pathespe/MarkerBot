delete from results where id > 0;
delete from questions where id > 0;
ALTER SEQUENCE questions_id_seq RESTART WITH 1;
ALTER SEQUENCE results_id_seq RESTART WITH 1;