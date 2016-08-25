INSERT INTO moduletags (module_ident, tagid) select module_ident, 8 from latest_modules where uuid in (

'1d39a348-071f-4537-85b6-c98912458c3c',
'4539ae23-1ccc-421e-9b25-843acbb6c4b0',
'5bcc0e59-7345-421d-8507-a1e4608685e8',
'8b89d172-2927-466f-8661-01abc7ccdba4',
'a31cd793-2162-4e9e-acb5-6e6bbd76a5fa',
'caa57dab-41c7-455e-bd6f-f443cda5519c'
);
