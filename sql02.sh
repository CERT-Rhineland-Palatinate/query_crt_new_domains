
echo "SELECT 
	DISTINCT(ci.NAME_VALUE)
    FROM 
        certificate_identity ci
    WHERE 
        reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower('%.rlp.de'))
" | psql -h crt.sh -p 5432 -U guest certwatch >out.txt 
