This project bitch crawl website data ,  parse website, and batch update mongodb data.  
use python multi process & thread

file name		| 		function
---|---
request.py		|	use python multi thread crawl website , and batch update mongodb data.  
crawl.py			|	open multi process run request.py procudure
conf.py			| 	site config infomation
ucp\_jd\_info.conf	| 	site original url config information
update.py		| 	batch update mongodb data demo procedure

if you want to crawl site data 
first, config conf.py file , include site name , data type, field xpath and so on.
second, run procedure crawl data ( python crawl.py site\_name)