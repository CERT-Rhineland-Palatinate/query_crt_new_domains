
echo "WITH ci AS (
    SELECT min(sub.CERTIFICATE_ID) ID,
           min(sub.ISSUER_CA_ID) ISSUER_CA_ID,
           array_agg(DISTINCT sub.NAME_VALUE) NAME_VALUES,
           x509_subjectName(sub.CERTIFICATE) SUBJECT_NAME,
           x509_notBefore(sub.CERTIFICATE) NOT_BEFORE,
           x509_notAfter(sub.CERTIFICATE) NOT_AFTER
        FROM (SELECT *
                  FROM certificate_and_identities cai
                  WHERE plainto_tsquery($1) @@ identities(cai.CERTIFICATE)
                      AND cai.NAME_VALUE ILIKE ('%' || $1 || '%')
                  LIMIT 10000
             ) sub
        GROUP BY sub.CERTIFICATE
)
SELECT ci.ISSUER_CA_ID,
        ca.NAME ISSUER_NAME,
        array_to_string(ci.NAME_VALUES, chr(10)) NAME_VALUE,
        ci.ID ID,
        le.ENTRY_TIMESTAMP,
        ci.NOT_BEFORE,
        ci.NOT_AFTER
    FROM ci
            LEFT JOIN LATERAL (
                SELECT min(ctle.ENTRY_TIMESTAMP) ENTRY_TIMESTAMP
                    FROM ct_log_entry ctle
                    WHERE ctle.CERTIFICATE_ID = ci.ID
            ) le ON TRUE,
         ca
    WHERE ci.ISSUER_CA_ID = ca.ID
    ORDER BY le.ENTRY_TIMESTAMP DESC;" | psql -h crt.sh -p 5432 -U guest certwatch >out.txt 
