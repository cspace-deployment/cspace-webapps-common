--
--
--

CREATE OR REPLACE FUNCTION utils.createObjectclassHierarchyTable() RETURNS void AS
$$
DECLARE
BEGIN
  IF NOT EXISTS ( SELECT relname
                  FROM pg_catalog.pg_class c
                       JOIN
                       pg_catalog.pg_namespace n
                       ON (n.oid = c.relnamespace)
               WHERE c.relname = 'objectclass_hierarchy'
                 AND n.nspname = 'utils' )
  THEN
    CREATE TABLE utils.objectclass_hierarchy (
       objectclasscsid text,
       objectclass text,
       parentid  text,
       nextcsid  text,
       objectclass_hierarchy text,
       csid_hierarchy text );

    CREATE INDEX uth_occsid_ndx on utils.objectclass_hierarchy ( objectclasscsid );
    CREATE INDEX uth_ocname_ndx on utils.objectclass_hierarchy ( objectclass );
  END IF;
END;
$$
LANGUAGE plpgsql

