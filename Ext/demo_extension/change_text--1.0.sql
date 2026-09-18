\echo Use "CREATE EXTENSION change_text" to load this file
CREATE FUNCTION change_text(dt text, symbol "char")
RETURNS text
AS 'MODULE_PATHNAME', 'change_text'
LANGUAGE C;