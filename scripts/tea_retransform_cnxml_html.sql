select now();
begin work;
-- Create a function that always returns the first non-NULL item
CREATE OR REPLACE FUNCTION public.first_agg ( anyelement, anyelement )
RETURNS anyelement LANGUAGE SQL IMMUTABLE STRICT AS $$
        SELECT $1;
$$;
 
-- And then wrap an aggregate around it
CREATE AGGREGATE public.FIRST (
        sfunc    = public.first_agg,
        basetype = anyelement,
        stype    = anyelement
);

-- Copy out the canonical CNXML 0.7 for each latest module, into a backup table
-- ryan confirms that all the content is listed as authored by user1 or manager1
CREATE TABLE index_cnxml_backup AS
    SELECT module_ident, fileid, filename
      FROM module_files  natural join latest_modules
      WHERE filename in ('index.cnxml','index_auto_generated.cnxml', 'index.cnxml.html')
      AND ('user1' = ANY (authors) OR 'manager1' = any (authors))
ORDER BY module_ident desc, fileid;

-- Delete the CNXML and the generated html from the files table
delete from module_files where filename in
('index.cnxml','index_auto_generated.cnxml', 'index.cnxml.html') and exists (
select 1 from index_cnxml_backup ic where module_ident = ic.module_ident);

-- reinsert the CNXML, there-by triggering index.cnxml.html generation
insert into module_files select * from index_cnxml_backup order by module_ident desc;
\d index_cnxml
commit;
select now(), count(*) from index_cnxml_backup;
