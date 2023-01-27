-- refreshObjectclassHierarchyTable
--
--  A function to keep the objectclass_hierarchy table up to date.
--  It is called from a nightly cron job

CREATE OR REPLACE FUNCTION utils.refreshObjectclassHierarchyTable() RETURNS void
AS $$
   insert into utils.refresh_log (msg) values ( 'Creating objectclass_hierarchy table' );
   select utils.createObjectclassHierarchyTable();

   insert into utils.refresh_log (msg) values ( 'Populating objectclass_hierarchy table' );
   select utils.populateObjectclassHierarchyTable();

   insert into utils.refresh_log (msg) values ( 'Updating objectclass_hierarchy table' );
   select utils.updateObjectclassHierarchyTable();

   insert into utils.refresh_log (msg) values ( 'All done' );
$$
LANGUAGE sql
