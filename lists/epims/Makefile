# see: https://www.epims.ogc.gov.uk/government-property-finder/Home.aspx

# no cool URLs, so built from a saved copy:
CSV=cache/PropertyHoldingExport_28-2-2017.csv

list.tsv:	$(CSV) map.py
	python3 map.py < $(CSV) > $@

clean:
	rm -f list.tsv
