
echo "SELECT ci.ISSUER_CA_ID,
        ca.NAME ISSUER_NAME,
        ci.NAME_VALUE NAME_VALUE,
        min(c.ID) MIN_CERT_ID,
        min(ctle.ENTRY_TIMESTAMP) MIN_ENTRY_TIMESTAMP,
        x509_notBefore(c.CERTIFICATE) NOT_BEFORE,
        x509_notAfter(c.CERTIFICATE) NOT_AFTER
    FROM ca,
        ct_log_entry ctle,
        certificate_identity ci,
        certificate c
    WHERE ci.ISSUER_CA_ID = ca.ID
        AND c.ID = ctle.CERTIFICATE_ID
        AND reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower('%.rlp.de'))
        AND ci.CERTIFICATE_ID = c.ID
    GROUP BY c.ID, ci.ISSUER_CA_ID, ISSUER_NAME, NAME_VALUE
    ORDER BY MIN_ENTRY_TIMESTAMP DESC, NAME_VALUE, ISSUER_NAME;
" | psql -h crt.sh -p 5432 -U guest certwatch >out.txt 
