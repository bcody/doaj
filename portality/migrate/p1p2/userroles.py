from portality import models

print "Migrating user accounts - adding publisher role"

batch = []
batch_size = 1000
for acc in models.Account.iterall():
    if len(acc.role) == 0:
        acc.add_role("publisher")
        batch.append(acc.data)
    if len(batch) >= batch_size:
        print "writing ", len(batch)
        models.Account.bulk(batch)
        batch = []

if len(batch) > 0:
    print "writing ", len(batch)
    models.Account.bulk(batch)
