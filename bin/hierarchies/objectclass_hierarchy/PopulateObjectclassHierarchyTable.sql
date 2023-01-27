-- populateObjectclassHierarchyTable
--
-- A function to insert the initial rows into the objectclass_hierarchy
-- table, which must already exist. The hierarchy columns will be built
-- up later by another procedure.

CREATE OR REPLACE FUNCTION utils.populateObjectclassHierarchyTable() RETURNS void AS
$$
  TRUNCATE TABLE utils.objectclass_hierarchy;

  WITH objectclass_hierarchyquery AS (
   SELECT
      h.name objectclasscsid,
      regexp_replace(cnc.refname, '^.*\)''(.*)''$', '\1') objectclass,
      rc.objectcsid broaderobjectclasscsid,
      regexp_replace(cnc2.refname, '^.*\)''(.*)''$', '\1') broaderobjectclass
    FROM public.concepts_common cnc
      INNER JOIN misc m ON (cnc.id=m.id AND m.lifecyclestate<>'deleted')
      LEFT OUTER JOIN hierarchy h ON (cnc.id = h.id AND h.primarytype='Conceptitem')
      LEFT OUTER JOIN public.relations_common rc ON (h.name = rc.subjectcsid)
      LEFT OUTER JOIN hierarchy h2 ON (h2.primarytype = 'Conceptitem'
                            AND rc.objectcsid = h2.name)
      LEFT OUTER JOIN concepts_common cnc2 ON (cnc2.id = h2.id)
      WHERE cnc.refname LIKE 'urn:cspace:pahma.cspace.berkeley.edu:conceptauthorities:name(objectclass)%'
    )
  INSERT INTO utils.objectclass_hierarchy
  SELECT DISTINCT
    objectclasscsid,
    objectclass,
    broaderobjectclasscsid AS parentcsid,
    broaderobjectclasscsid AS nextcsid,
    objectclass AS objectclass_hierarchy,
    objectclasscsid AS csid_hierarchy
  FROM  objectclass_hierarchyquery;
$$
LANGUAGE sql
