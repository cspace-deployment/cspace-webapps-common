for m in bampfa cinefiles pahma
  do
    rm -f ${m}_extract.csv ${m}_freq_search.csv ${m}_dates_raw.csv  ${m}_dates.csv
    for f in ~/projects/search_$m/db/*.gz
      do
        echo "procesing $f..."
        gunzip -c $f > tmp
        sqlite3 tmp.db < tmp
        echo 'select query_params from searches ;' | sqlite3 tmp.db | perl -ne 's/\!.*//; print unless /utf8:/' >> ${m}_extract.csv
        echo 'select created_at from searches ;' | sqlite3 tmp.db | cut -f1 -d " " >> ${m}_dates_raw.csv 
	rm tmp tmp.db
    done
    sort ${m}_dates_raw.csv| uniq -c > ${m}_dates.csv
    sort ${m}_terms.csv | uniq -c | sort -rn | head -1000 > ${m}_freq_search.csv 
    python blacklight_stats.py ${m}_extract.csv > ${m}_terms.csv          
    tail -3 ${m}_terms.csv
  done
