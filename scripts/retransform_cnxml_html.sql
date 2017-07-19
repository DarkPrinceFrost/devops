select now();
begin work;
create temp table index_cnxml as select module_ident, first(fileid) as fileid, 'index.cnxml'::text  as filename from (select module_ident, filename, fileid from module_files  natural join latest_modules where filename in ('index.cnxml','index_auto_generated.cnxml') order by module_ident desc, fileid desc) as idxs group by module_ident order by module_ident desc;
delete from module_files where filename in ('index.cnxml','index_auto_generated.cnxml', 'index.cnxml.html') and exists ( select 1 from index_cnxml ic where module_ident = ic.module_ident);
insert into module_files select * from index_cnxml order by module_ident desc;
\d index_cnxml
commit;
