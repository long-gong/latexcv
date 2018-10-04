import bibtexparser

with open('./data/long_gong_pub.bib') as bib_file:
    bib_db = bibtexparser.load(bib_file)
    for b in sorted(bib_db.entries, key=lambda x: -int(x["year"])):
        #print "-", b["ID"]
        if b['author'].startswith('{\\bf'):
            print "-", b["ID"]

